# analysis.py
import os
import re
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from config import GAMING_PLATFORMS
from improved_semantic_correction import advanced_semantic_correction
from utils import extract_numbers

def test_semantic_correction():
    """
    Teste la fonction de correction sémantique avec des exemples d'erreurs OCR.
    """
    test_cases = [
        "This is a playstation game",
        "Found a PIay5tation controller at the store",
        "X80X games on sale",
        "The game works on X-box",
        "The game is available on P C",
        "This is a special Nlntend0 edition",
        "Nintemdo Switch game",
        "Designed for Playststion and XB0X",
        "This works on Stearn for PC users",
        "Compatible with plehstatien"
    ]
    
    print("Test de la correction sémantique :")
    print("===================================")
    for text in test_cases:
        corrected = advanced_semantic_correction(text)
        if text.lower() != corrected.lower():
            print(f"Original : {text}")
            print(f"Corrigé : {corrected}")
            
            platforms_found = [platform for platform in GAMING_PLATFORMS.keys() if platform in corrected.lower()]
            print(f"Plateforme(s) détectée(s) : {', '.join(platforms_found)}")
            print("---")
        else:
            print(f"Aucune correction nécessaire : {text}")
            print("---")
    print()

def analyze_ocr_results(dfs, ground_truth_labels=None):
    """
    Analyse les résultats OCR et évalue les performances.
    
    Args:
        dfs (dict): Dictionnaire de DataFrames avec le nom du filtre comme clé
        ground_truth_labels (dict, optionnel): Labels de référence
        
    Returns:
        pd.DataFrame: Résumé des résultats
    """
    if not dfs:
        print("Aucun résultat OCR à analyser")
        return None
    
    results = {}
    
    for filter_name, df in dfs.items():
        if df.empty:
            continue
        
        clean_filter_name = filter_name.split('_')[0]
        df['corrected_text'] = df['extracted_text'].apply(advanced_semantic_correction)
        
        df['has_platform_original'] = df['extracted_text'].apply(
            lambda x: any(platform in str(x).lower() for platform in GAMING_PLATFORMS.keys()) 
            if not pd.isna(x) else False
        )
        df['has_platform_corrected'] = df['corrected_text'].apply(
            lambda x: any(platform in str(x).lower() for platform in GAMING_PLATFORMS.keys()) 
            if not pd.isna(x) else False
        )
        
        platform_count_original = df['has_platform_original'].sum()
        platform_count_corrected = df['has_platform_corrected'].sum()
        platform_improvement = platform_count_corrected - platform_count_original
        
        df['extracted_numbers'] = df['extracted_text'].apply(extract_numbers)
        df['number_count'] = df['extracted_numbers'].apply(len)
        total_numbers = df['number_count'].sum()
        
        df['text_length'] = df['extracted_text'].apply(lambda x: len(str(x)) if not pd.isna(x) else 0)
        avg_text_length = df['text_length'].mean()
        avg_processing_time = df['processing_time'].mean() if 'processing_time' in df.columns else np.nan
        
        results[clean_filter_name] = {
            'platform_count': platform_count_corrected,
            'platform_count_original': platform_count_original,
            'platform_improvement': platform_improvement,
            'platform_percentage': (platform_count_corrected / len(df)) * 100,
            'total_numbers': total_numbers,
            'avg_numbers_per_image': total_numbers / len(df),
            'avg_text_length': avg_text_length,
            'avg_processing_time': avg_processing_time,
            'total_images': len(df)
        }
        
        for platform in GAMING_PLATFORMS.keys():
            platform_count = df['corrected_text'].apply(
                lambda x: platform in str(x).lower() if not pd.isna(x) else False
            ).sum()
            results[clean_filter_name][f'platform_{platform}'] = platform_count
        
        if ground_truth_labels:
            metrics = calculate_metrics(df, ground_truth_labels)
            results[clean_filter_name].update({
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1': metrics['f1'],
                'evaluated_images': metrics['evaluated_images']
            })
            
            print(f"Métriques pour {clean_filter_name} :")
            print(f"  F1 : {metrics['f1']:.4f}, Précision : {metrics['precision']:.4f}, Rappel : {metrics['recall']:.4f}")
            print(f"  Accuracy : {metrics['accuracy']:.4f}")
            print(f"  Evalué sur {metrics['evaluated_images']} images")
            print()
    
    results_df = pd.DataFrame(results).T
    if ground_truth_labels and 'f1' in results_df.columns:
        results_df = results_df.sort_values('f1', ascending=False)
    else:
        results_df = results_df.sort_values('platform_count', ascending=False)
    
    return results_df

def calculate_metrics(df, ground_truth_labels):
    """
    Calcule les métriques d'évaluation pour la détection de plateforme.
    
    Args:
        df (pd.DataFrame): DataFrame des résultats OCR
        ground_truth_labels (dict): Labels de référence
        
    Returns:
        dict: Dictionnaire des métriques
    """
    if 'corrected_text' not in df.columns:
        df['corrected_text'] = df['extracted_text'].apply(advanced_semantic_correction)
    
    df['predicted_platform'] = 'unknown'
    
    for idx, row in df.iterrows():
        if not pd.isna(row['corrected_text']) and isinstance(row['corrected_text'], str):
            text = row['corrected_text'].lower()
            detected_platforms = [platform for platform in GAMING_PLATFORMS.keys() if platform in text]
            if detected_platforms:
                df.loc[idx, 'predicted_platform'] = detected_platforms[0]
    
    evaluation_data = []
    for _, row in df.iterrows():
        filename = row['filename']
        if '/' in filename or '\\' in filename:
            filename = os.path.basename(filename)
        predicted = row['predicted_platform']
        
        if filename in ground_truth_labels:
            true_label = ground_truth_labels[filename]
            evaluation_data.append({
                'filename': filename,
                'true_label': true_label,
                'predicted': predicted,
                'correct': predicted == true_label
            })
    
    if not evaluation_data:
        return {
            'accuracy': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0,
            'evaluated_images': 0
        }
    
    eval_df = pd.DataFrame(evaluation_data)
    y_true = eval_df['true_label'].values
    y_pred = eval_df['predicted'].values
    
    try:
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        accuracy = accuracy_score(y_true, y_pred)
    except Exception as e:
        print(f"Erreur lors du calcul des métriques : {str(e)}")
        precision, recall, f1, accuracy = 0, 0, 0, 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'evaluated_images': len(eval_df)
    }

def recommend_filters(results_df):
    """
    Recommande les meilleurs filtres de prétraitement en fonction des résultats.
    
    Args:
        results_df (pd.DataFrame): DataFrame récapitulatif des résultats
    """
    if results_df is None or results_df.empty:
        print("Aucun résultat pour générer une recommandation")
        return
    
    print("\nRecommandation des meilleurs filtres :")
    print("======================================")
    
    has_metrics = all(col in results_df.columns for col in ['precision', 'recall', 'f1'])
    
    if has_metrics:
        results_df['score'] = (
            0.6 * results_df['f1'] + 
            0.2 * results_df['precision'] + 
            0.2 * results_df['recall']
        )
        results_df = results_df.sort_values('score', ascending=False)
        print("\nTop 5 filtres basés sur le F1 score :")
    else:
        results_df['score'] = (
            0.5 * (results_df['platform_percentage'] / results_df['platform_percentage'].max()) + 
            0.3 * (results_df['total_numbers'] / results_df['total_numbers'].max() if results_df['total_numbers'].max() > 0 else 0) + 
            0.2 * (results_df['avg_text_length'] / results_df['avg_text_length'].max() if results_df['avg_text_length'].max() > 0 else 0)
        )
        results_df = results_df.sort_values('score', ascending=False)
        print("\nTop 5 filtres basés sur la détection de plateforme :")
    
    for i, (filter_name, row) in enumerate(results_df.head(5).iterrows()):
        print(f"{i+1}. {filter_name} (Score : {row['score']:.2f})")
        if has_metrics:
            print(f"   - F1 Score : {row['f1']:.3f}")
            print(f"   - Précision : {row['precision']:.3f}")
            print(f"   - Rappel : {row['recall']:.3f}")
            print(f"   - Accuracy : {row['accuracy']:.3f}")
            print(f"   - Évalué sur : {row['evaluated_images']} images")
        print(f"   - Plateformes détectées : {row['platform_count']} ({row['platform_percentage']:.1f}%)")
        print(f"   - Nombres extraits : {row['total_numbers']} (moy. {row['avg_numbers_per_image']:.1f} par image)")
        print(f"   - Longueur moyenne du texte : {row['avg_text_length']:.1f} caractères")
        if 'avg_processing_time' in row and not pd.isna(row['avg_processing_time']):
            print(f"   - Temps de traitement moyen : {row['avg_processing_time']:.2f} secondes")
        print()
    
    best_filter = results_df.index[0]
    print("\nRecommandation finale :")
    if has_metrics:
        print(f"Le meilleur filtre de prétraitement selon le F1 score est : {best_filter}")
    else:
        print(f"Le meilleur filtre de prétraitement semble être : {best_filter}")
