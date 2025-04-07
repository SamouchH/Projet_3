# model_training_ml.py (version modifiée)
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from vectorizers import get_tfidf_vectorizer
from text_preprocessing import clean_text
from collections import Counter

def train_multiple_models(df, ground_truth, test_size=0.15, val_size=0.15, random_state=42):
    """
    Entraîne plusieurs modèles de classification ML classiques et sélectionne le meilleur modèle basé sur le F1-score.
    
    Args:
        df (pd.DataFrame): Données OCR contenant 'filename' et 'text' (texte OCR brut ou corrigé)
        ground_truth (dict): Dictionnaire associant le nom de l'image à sa plateforme
        test_size (float): Proportion du jeu de test
        val_size (float): Proportion du jeu de validation (par rapport au train+val)
        random_state (int): Graine aléatoire
        
    Returns:
        best_pipeline: Pipeline du meilleur modèle
        results: Dictionnaire avec les métriques pour chaque modèle
        X_test, y_test: Jeu de test pour évaluation finale
    """
    df = df.copy()
    # Extraction du nom de base du fichier
    df['filename_base'] = df['filename'].apply(lambda x: os.path.basename(x))
    df['platform'] = df['filename_base'].apply(lambda x: ground_truth.get(x, None))
    df = df[df['platform'].notna()]
    if df.empty:
        print("Aucune donnée avec label pour l'entraînement.")
        return None, None, None

    # Utiliser 'corrected_text' si disponible, sinon 'extracted_text'
    if 'corrected_text' in df.columns:
        df['text'] = df['corrected_text']
    else:
        df['text'] = df['extracted_text']
    
    # Nettoyage du texte et remplacement des valeurs manquantes par une chaîne vide
    df['text'] = df['text'].apply(clean_text).fillna("")
    
    X = df['text']
    y = df['platform']
    
    # Vérifier la distribution des labels
    label_counts = Counter(y)
    print("Distribution des labels:", label_counts)
    if min(label_counts.values()) < 2:
        stratify_arg = None
        print("Attention : certaines classes ont moins de 2 échantillons. Désactivation de la stratification pour le split.")
    else:
        stratify_arg = y
    
    # Découpage en train+val et test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_arg
    )
    
    # Pour le second split, vérifier la distribution dans y_train_val
    label_counts_train_val = Counter(y_train_val)
    if min(label_counts_train_val.values()) < 2:
        stratify_arg_train = None
        print("Attention : dans le train+val, certaines classes ont moins de 2 échantillons. Désactivation de la stratification pour le split train/val.")
    else:
        stratify_arg_train = y_train_val

    # Découpage du jeu train+val en train et validation
    val_relative_size = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative_size, random_state=random_state, stratify=stratify_arg_train
    )
    
    print(f"Train: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
    
    # Définition des modèles candidats
    candidate_models = {
        "Logistic Regression": LogisticRegression(random_state=random_state, max_iter=1000),
        "SVM": SVC(probability=True, random_state=random_state),
        "Random Forest": RandomForestClassifier(random_state=random_state),
        "Gradient Boosting": GradientBoostingClassifier(random_state=random_state)
    }
    
    vectorizer = get_tfidf_vectorizer()
    best_f1 = -1
    best_pipeline = None
    results = {}
    
    for name, classifier in candidate_models.items():
        pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', classifier)
        ])
        # Entraînement du modèle sur le jeu d'entraînement
        pipeline.fit(X_train, y_train)
        # Prédictions sur le jeu de validation
        y_val_pred = pipeline.predict(X_val)
        f1 = f1_score(y_val, y_val_pred, average='weighted')
        acc = accuracy_score(y_val, y_val_pred)
        recall_val = recall_score(y_val, y_val_pred, average='weighted', zero_division=0)
        results[name] = {"f1": f1, "accuracy": acc, "recall": recall_val}
        print(f"Modèle: {name} - Validation F1: {f1:.4f}, Accuracy: {acc:.4f}, Recall: {recall_val:.4f}")
        if f1 > best_f1:
            best_f1 = f1
            best_pipeline = pipeline
    
    print(f"\nMeilleur modèle sélectionné: {best_pipeline.named_steps['classifier'].__class__.__name__} avec F1 = {best_f1:.4f}")
    
    # Évaluation du meilleur modèle sur le jeu de test
    y_test_pred = best_pipeline.predict(X_test)
    test_f1 = f1_score(y_test, y_test_pred, average='weighted')
    test_acc = accuracy_score(y_test, y_test_pred)
    test_recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
    print("\n=== Évaluation sur le jeu de test du meilleur modèle ===")
    print(classification_report(y_test, y_test_pred, zero_division=0))
    print(f"Test Accuracy: {test_acc:.4f}, Test Recall: {test_recall:.4f}")
    
    return best_pipeline, results, X_test, y_test
