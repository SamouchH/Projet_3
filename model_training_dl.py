# model_training_dl.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
from text_preprocessing import clean_text

def train_transformer_model(df, ground_truth, model_name="distilbert-base-uncased", num_labels=None, test_size=0.15, val_size=0.15, random_state=42):
    """
    Entraîne un modèle de classification basé sur un transformeur (ex. DistilBERT) pour la classification de texte.
    
    Args:
        df (pd.DataFrame): Données OCR contenant 'filename' et 'text'
        ground_truth (dict): Dictionnaire associant le nom de l'image à sa plateforme
        model_name (str): Nom du modèle pré-entraîné à utiliser
        num_labels (int): Nombre de classes (déduit si None)
        test_size (float): Proportion du jeu de test
        val_size (float): Proportion du jeu de validation
        random_state (int): Graine aléatoire
        
    Returns:
        model, tokenizer, trainer: Modèle entraîné, tokenizer et instance du Trainer
    """
    df = df.copy()
    df['filename_base'] = df['filename'].apply(lambda x: os.path.basename(x))
    df['platform'] = df['filename_base'].apply(lambda x: ground_truth.get(x, None))
    df = df[df['platform'].notna()]
    if df.empty:
        print("Aucune donnée avec label pour l'entraînement DL.")
        return None, None, None
    
    # Utiliser le texte corrigé si disponible
    if 'corrected_text' in df.columns:
        df['text'] = df['corrected_text']
    else:
        df['text'] = df['extracted_text']
    df['text'] = df['text'].apply(clean_text)
    
    # Création d'un mapping des labels
    labels = sorted(df['platform'].unique())
    label2id = {label: idx for idx, label in enumerate(labels)}
    id2label = {idx: label for label, idx in label2id.items()}
    
    if num_labels is None:
        num_labels = len(labels)
    
    df['label'] = df['platform'].apply(lambda x: label2id[x])
    
    # Séparation train, validation et test
    X = df['text'].tolist()
    y = df['label'].tolist()
    train_texts, test_texts, train_labels, test_labels = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    val_relative_size = val_size / (1 - test_size)
    train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=val_relative_size, random_state=random_state, stratify=train_labels)
    
    # Chargement du tokenizer et du modèle
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels, id2label=id2label, label2id=label2id)
    
    # Tokenization des textes
    def tokenize_function(texts):
        return tokenizer(texts, padding="max_length", truncation=True, max_length=128)
    
    train_encodings = tokenize_function(train_texts)
    val_encodings = tokenize_function(val_texts)
    test_encodings = tokenize_function(test_texts)
    
    # Création d'un dataset personnalisé
    class OCRDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels
        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item
        def __len__(self):
            return len(self.labels)
    
    train_dataset = OCRDataset(train_encodings, train_labels)
    val_dataset = OCRDataset(val_encodings, val_labels)
    test_dataset = OCRDataset(test_encodings, test_labels)
    
    # Configuration de l'entraînement
    training_args = TrainingArguments(
        output_dir="./results_transformer",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir="./logs_transformer",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
    )
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        accuracy = (predictions == labels).mean()
        return {"accuracy": accuracy}
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Entraînement du modèle
    trainer.train()
    
    # Évaluation sur le jeu de test
    test_result = trainer.evaluate(test_dataset)
    print("=== Évaluation sur le jeu de test (DL) ===")
    print(test_result)
    
    return model, tokenizer, trainer
