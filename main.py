# main.py (version mise à jour)
from data_loader import load_ocr_results, load_ground_truth
from analysis import test_semantic_correction, analyze_ocr_results, recommend_filters
from visualization import visualize_results
from cover_analysis import analyze_game_covers
from logo_detection import detect_logo_in_image, detect_logos_in_game_cover
def main():
    """
    Main function to execute the OCR Analyzer program.
    This program performs the following tasks:
    1. Tests semantic correction functionality.
    2. Loads ground truth labels from a specified directory.
    3. Loads OCR results from a specified directory.
    4. Analyzes OCR results, optionally using ground truth labels for evaluation.
    5. Visualizes the analysis results and recommends the best preprocessing filter.
    6. Allows the user to train a machine learning or deep learning model based on the best filter's data.
    7. Performs logo detection on video game covers using specified logo templates.
    Steps:
    - Loads and processes OCR results and ground truth labels.
    - Analyzes OCR results with or without reference labels.
    - Visualizes results and recommends the best preprocessing filter.
    - Provides options to train a model using classical ML, deep learning, or a comparison of ML methods.
    - Detects logos on video game covers using a specified detection threshold.
    Directories:
    - `ocr_results`: Directory containing OCR result CSV files.
    - `data/batchs_csv`: Directory containing ground truth label CSV files.
    - `plots`: Directory to save generated visualizations.
    - `images_folder`: Directory containing video game cover images.
    - `logo_folder`: Directory containing logo templates for detection.
    User Input:
    - Choice of model type to train:
        1. Classical machine learning.
        2. Deep learning.
        3. Comparison of multiple ML methods.
    Outputs:
    - Analysis results summary.
    - Visualizations of OCR analysis.
    - Recommended preprocessing filter.
    - Trained model (based on user choice).
    - Detected logos on video game covers.
    Note:
    Ensure the required directories and files are properly set up before running the program.
    """
    print("OCR Analyzer - Comparaison des techniques de prétraitement pour l'OCR")
    print("=====================================================================")
    
    # Test de la correction sémantique
    test_semantic_correction()
    
    # Définition des répertoires
    ocr_dir = "ocr_results"       # Répertoire contenant les CSV OCR
    gt_dir = "data/batchs_csv"    # Répertoire contenant les labels de référence
    plots_dir = "plots"           # Répertoire pour sauvegarder les graphiques
    
    print("\nChargement des labels de référence...")
    ground_truth = load_ground_truth(gt_dir)
    
    print("\nChargement des résultats OCR...")
    ocr_results = load_ocr_results(ocr_dir)
    
    if not ocr_results:
        print("Aucun résultat OCR à analyser. Fin du programme.")
        return
    
    print("\nAnalyse des résultats OCR...")
    if ground_truth:
        print(f"Utilisation des labels de référence pour {len(ground_truth)} images étiquetées")
        results = analyze_ocr_results(ocr_results, ground_truth)
    else:
        print("Aucun label de référence trouvé. Analyse sans métriques d'évaluation.")
        results = analyze_ocr_results(ocr_results)
    
    if results is not None:
        print("\nRésumé des résultats :")
        print("=====================")
        print(results)
        
        print("\nCréation des visualisations...")
        visualize_results(results, plots_dir)
        
        recommend_filters(results)
        
        # Récupération du meilleur filtre recommandé
        best_filter = results.index[0]
        print(f"\nLe meilleur filtre recommandé est : {best_filter}")
        
        # Sélection des DataFrames OCR correspondant au meilleur filtre
        selected_dfs = [df for key, df in ocr_results.items() if key.startswith(best_filter)]
        if selected_dfs:
            import pandas as pd
            best_filter_df = pd.concat(selected_dfs, ignore_index=True)
            print(f"Nombre d'enregistrements issus du filtre '{best_filter}' : {len(best_filter_df)}")
            
            # Choix du type de modèle à entraîner
            choice = input("Choisissez le type de modèle à entraîner (1: ML classique, 2: Deep Learning, 3: Comparaison de méthodes ML): ")
            if choice.strip() == "2":
                from model_training_dl import train_transformer_model
                model, tokenizer, trainer = train_transformer_model(best_filter_df, ground_truth)
            elif choice.strip() == "3":
                from model_training_ml import train_multiple_models
                best_pipeline, ml_results, X_test, y_test = train_multiple_models(best_filter_df, ground_truth)
            else:
                from model_training_ml import train_classical_model
                pipeline, X_test, y_test = train_classical_model(best_filter_df, ground_truth)
                from evaluation import evaluate_classical_model
                evaluate_classical_model(pipeline, X_test, y_test)
        else:
            print(f"Aucune donnée OCR correspondant au meilleur filtre : {best_filter}")
    else:
        print("L'analyse n'a pas permis de produire des résultats.")
    
    # Nouvelle étape : Analyse des logos sur les couvertures de jeux vidéo
    print("\nAnalyse des couvertures de jeux pour détecter des logos...")
    # Supposons que vos couvertures soient dans le dossier "cover_folder" et vos logos dans "logo_folder"
    from cover_analysis import analyze_game_covers
    cover_folder = "images_folder"  # Dossier contenant les images de couverture
    logo_folder = "logo_folder"    # Dossier contenant les logos
    logo_threshold = 0.7           # Seuil de détection (à ajuster)
    
    logo_results = analyze_game_covers(cover_folder, logo_folder, logo_threshold)
    for cover, detections in logo_results.items():
        print(f"Couverture: {cover}")
        if detections:
            for logo, score in detections.items():
                print(f"  Logo détecté: {logo} (score: {score:.2f})")
        else:
            print("  Aucun logo détecté.")
    
    print("\nTerminé!")
    print("=====================================================================")

if __name__ == "__main__":
    main()


import sys
import os

current_folder = os.path.abspath(".")

with open("modules_utilises.txt", "w") as f:
    for mod in sys.modules.values():
        fichier = getattr(mod, "__file__", "")
        if fichier and fichier.endswith(".py") and fichier.startswith(current_folder):
            if "site-packages" not in fichier and "projet_3_env" not in fichier:
                f.write(f"{fichier}\n")

print("Liste filtrée des modules enregistrée dans 'modules_utilises.txt'")

