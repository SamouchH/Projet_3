# main.py
from data_loader import load_ocr_results, load_ground_truth
from analysis import test_semantic_correction, analyze_ocr_results, recommend_filters
from visualization import visualize_results

def main():
    print("OCR Analyzer - Comparaison des techniques de prétraitement pour l'OCR")
    print("=====================================================================")
    
    # (Étapes d'analyse OCR, visualisations et entraînement...)
    # [Votre code existant pour OCR et entraînement ici]
    
    # Nouvelle étape : Analyse améliorée des logos sur les couvertures de jeux vidéo
    print("\nAnalyse des couvertures de jeux pour détecter des logos (méthode améliorée ORB avec vote)...")
    cover_folder = "images_folder"   # Dossier contenant les images de couverture
    logo_folder = "logo_folder"     # Dossier contenant les logos
    ratio_test = 0.75
    min_match_count = 10
    nfeatures_orb = 3000
    
    from cover_analysis import analyze_game_covers
    logo_results = analyze_game_covers(cover_folder, logo_folder, ratio_test, min_match_count, nfeatures_orb)
    
    for cover, detections in logo_results.items():
        print(f"Couverture: {cover}")
        if detections:
            for logo, corners in detections.items():
                print(f"  Logo détecté: {logo} (coins: {corners})")
        else:
            print("  Aucun logo détecté.")
    
    # Calcul des métriques de détection (globales)
    from logo_metrics import compute_logo_detection_metrics, compute_logo_classification_metrics
    detection_metrics = compute_logo_detection_metrics(logo_results)
    print("\n=== Statistiques de détection des logos ===")
    print(f"Nombre total de couvertures analysées: {detection_metrics['total_covers']}")
    print(f"Nombre de couvertures avec au moins un logo: {detection_metrics['covers_with_logo']} ({detection_metrics['percentage_with_logo']:.2f}%)")
    
    # Charger la ground truth
    ground_truth = load_ground_truth("data/batchs_csv")
    
    # Définir le mapping des logos vers les catégories
    logo_category_mapping = {
       "nintendo_wii": "nintendo",
       "nintendo_wiiu": "nintendo",
       "nintendo_switch": "nintendo",
       "nintendo_3ds": "nintendo",
       "gamecube": "nintendo",
       "supernintendo": "nintendo",
       "gameboyadvance": "nintendo",
       "gameboycolor": "nintendo",
       "dreamcast": "sega",
       "sega_saturn": "sega",
       "mega_drive": "sega",
       "playstation_1": "playstation",
       "playstation_2": "playstation",
       "xbox_1": "xbox",
       "xbox_2": "xbox"
    }
    
    classification_metrics = compute_logo_classification_metrics(logo_results, ground_truth, logo_category_mapping, default_prediction="none")
    print("\n=== Métriques de classification pour la détection des logos ===")
    print(f"Accuracy: {classification_metrics['accuracy']:.2f}")
    print(f"Precision: {classification_metrics['precision']:.2f}")
    print(f"Recall: {classification_metrics['recall']:.2f}")
    print(f"F1 Score: {classification_metrics['f1']:.2f}")
    print("\nRapport détaillé :\n", classification_metrics["report"])
    
    print("\nTerminé!")
    print("=====================================================================")

if __name__ == "__main__":
    main()


import sys
import os

current_folder = os.path.abspath(".")

with open("modules_utilises_images_only.txt", "w") as f:
    for mod in sys.modules.values():
        fichier = getattr(mod, "__file__", "")
        if fichier and fichier.endswith(".py") and fichier.startswith(current_folder):
            if "site-packages" not in fichier and "projet_3_env" not in fichier:
                f.write(f"{fichier}\n")

print("Liste filtrée des modules enregistrée dans 'modules_utilises_images_only.txt'")