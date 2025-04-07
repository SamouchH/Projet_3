# visualization.py
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def visualize_results(results_df, output_dir="plots"):
    """
    Crée des visualisations des résultats OCR.
    
    Args:
        results_df (pd.DataFrame): DataFrame récapitulatif des résultats
        output_dir (str): Répertoire où enregistrer les graphiques
    """
    if results_df is None or results_df.empty:
        print("Aucun résultat à visualiser")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('ggplot')
    sns.set(font_scale=1.2)
    
    # 1. Taux de détection des plateformes
    plt.figure(figsize=(12, 8))
    ax = results_df['platform_percentage'].sort_values(ascending=False).plot(kind='bar')
    ax.set_title('Taux de détection par filtre de prétraitement')
    ax.set_ylabel('Taux de détection (%)')
    ax.set_xlabel('Filtre de prétraitement')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_platform_detection_rate.png'))
    
    # 2. Détection originale vs corrigée
    if 'platform_count_original' in results_df.columns:
        width = 0.35
        x = np.arange(len(results_df.index))
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width/2, results_df['platform_count_original'], width, label='Texte original')
        ax.bar(x + width/2, results_df['platform_count'], width, label='Après correction sémantique')
        ax.set_title('Nombre d\'images avec référence de plateforme détectée')
        ax.set_ylabel('Nombre')
        ax.set_xlabel('Filtre de prétraitement')
        ax.set_xticks(x)
        ax.set_xticklabels(results_df.index, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '2_original_vs_corrected.png'))
    
    # 3. Répartition par plateforme
    platform_cols = [col for col in results_df.columns if col.startswith('platform_') 
                    and col not in ['platform_count', 'platform_count_original', 'platform_improvement', 'platform_percentage']]
    if platform_cols:
        top_filters = results_df.head(10)
        platform_data = top_filters[platform_cols]
        platform_data.columns = [col.replace('platform_', '') for col in platform_data.columns]
        plt.figure(figsize=(14, 8))
        platform_data.plot(kind='bar', stacked=True, colormap='viridis')
        plt.title('Répartition des types de plateformes détectées')
        plt.ylabel('Nombre')
        plt.xlabel('Filtre de prétraitement')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Type de plateforme')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '3_platform_breakdown.png'))
    
    # 4. Comparaison de la longueur des textes
    plt.figure(figsize=(14, 8))
    ax = results_df['avg_text_length'].plot(kind='bar', color='purple')
    ax.set_title('Longueur moyenne du texte extrait')
    ax.set_ylabel('Nombre de caractères')
    ax.set_xlabel('Filtre de prétraitement')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '4_text_length.png'))
    
    # 5. Comparaison du nombre de nombres extraits
    plt.figure(figsize=(14, 8))
    ax = results_df['avg_numbers_per_image'].plot(kind='bar', color='green')
    ax.set_title('Nombre moyen de valeurs numériques détectées par image')
    ax.set_ylabel('Nombre moyen')
    ax.set_xlabel('Filtre de prétraitement')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_number_extraction.png'))
    
    # 6. Temps de traitement (si disponible)
    if 'avg_processing_time' in results_df.columns and not results_df['avg_processing_time'].isna().all():
        plt.figure(figsize=(14, 8))
        ax = results_df['avg_processing_time'].plot(kind='bar', color='orange')
        ax.set_title('Temps de traitement moyen par image')
        ax.set_ylabel('Temps (secondes)')
        ax.set_xlabel('Filtre de prétraitement')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '6_processing_time.png'))
    
    # 7. Métriques d'évaluation (si disponibles)
    if all(col in results_df.columns for col in ['precision', 'recall', 'f1', 'accuracy']):
        plt.figure(figsize=(14, 8))
        metrics_df = results_df[['precision', 'recall', 'f1', 'accuracy']].sort_values('f1', ascending=False).head(10)
        metrics_df.plot(kind='bar')
        plt.title('Métriques d\'évaluation par filtre')
        plt.ylabel('Score')
        plt.xlabel('Filtre de prétraitement')
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '7_evaluation_metrics.png'))
        
        # 8. Comparaison des F1 scores
        plt.figure(figsize=(14, 8))
        top_10 = results_df.sort_values('f1', ascending=False).head(10)
        ax = top_10['f1'].plot(kind='bar', color='green')
        ax.set_title('F1 Score par filtre (Top 10)')
        ax.set_ylabel('F1 Score')
        ax.set_xlabel('Filtre de prétraitement')
        plt.ylim(0, 1.0)
        for i, v in enumerate(top_10['f1']):
            ax.text(i, v + 0.02, f'{v:.2f}', ha='center')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '8_f1_comparison.png'))
    
    print(f"{len(os.listdir(output_dir))} graphiques sauvegardés dans {output_dir}")
