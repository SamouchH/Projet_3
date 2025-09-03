# de_nouveau.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

def train_model(df, ground_truth, test_size=0.15, val_size=0.15, random_state=42):
    """
    Entraîne un modèle de classification à partir des données OCR issues du meilleur filtrage.
    
    Args:
        df (pd.DataFrame): Données OCR (doit contenir au moins les colonnes 'filename' et 'corrected_text' ou 'extracted_text')
        ground_truth (dict): Dictionnaire associant le nom de l'image à sa plateforme (label de référence)
        test_size (float): Proportion du jeu de test
        val_size (float): Proportion du jeu de validation (relative au reste après extraction du test)
        random_state (int): Graine pour le tirage aléatoire
        
    Returns:
        clf: Le modèle entraîné
        vectorizer: L'objet de vectorisation utilisé
    """
    df = df.copy()
    # On récupère le nom de fichier sans chemin
    df['filename_base'] = df['filename'].apply(lambda x: os.path.basename(x))
    df['platform'] = df['filename_base'].apply(lambda x: ground_truth.get(x, None))
    
    # On ne garde que les lignes pour lesquelles un label est disponible
    df = df[df['platform'].notna()]
    if df.empty:
        print("Aucune donnée avec label de référence pour l'entraînement.")
        return None, None
    
    # Utilisation de 'corrected_text' si présente, sinon 'extracted_text'
    if 'corrected_text' in df.columns:
        df['text'] = df['corrected_text']
    else:
        df['text'] = df['extracted_text']
    
    df = df[df['text'].notna()]
    
    X = df['text']
    y = df['platform']
    
    # Découpage en jeu train+val et test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Découpage du jeu train+val en entraînement et validation
    val_relative_size = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative_size, random_state=random_state, stratify=y_train_val
    )
    
    print(f"Entraînement sur {len(X_train)} échantillons, validation sur {len(X_val)} et test sur {len(X_test)}")
    
    # Vectorisation du texte avec TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)
    
    # Entraînement d'un modèle de régression logistique
    clf = LogisticRegression(random_state=random_state, max_iter=1000)
    clf.fit(X_train_vec, y_train)
    
    # Prédiction et évaluation sur le jeu de validation et de test
    y_val_pred = clf.predict(X_val_vec)
    y_test_pred = clf.predict(X_test_vec)
    
    print("=== Évaluation sur le jeu de validation ===")
    print(classification_report(y_val, y_val_pred))
    print("=== Évaluation sur le jeu de test ===")
    print(classification_report(y_test, y_test_pred))
    print("Accuracy sur le jeu de test :", accuracy_score(y_test, y_test_pred))
    
    return clf, vectorizer
