# logo_metrics.py
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

def compute_logo_detection_metrics(logo_results):
    """
    Calcule des métriques globales simples à partir des résultats de détection.
    
    Args:
        logo_results (dict): {cover_filename: detections} où detections est un dict {logo: corners}.
    
    Returns:
        dict: Dictionnaire avec total, covers_with_logo et pourcentage.
    """
    total = len(logo_results)
    covers_with_logo = sum(1 for detections in logo_results.values() if detections)
    
    metrics = {
        "total_covers": total,
        "covers_with_logo": covers_with_logo,
        "percentage_with_logo": (covers_with_logo / total * 100) if total > 0 else 0,
    }
    return metrics

def compute_logo_classification_metrics(logo_results, ground_truth, logo_category_mapping, default_prediction="none"):
    """
    Compare la catégorie prédite à partir des logos détectés (en appliquant un système de vote) aux labels de référence.
    
    Args:
        logo_results (dict): {cover_filename: detections} où detections est un dict {logo: corners}.
        ground_truth (dict): {cover_filename: true_category}.
        logo_category_mapping (dict): Mapping de logo à catégorie.
        default_prediction (str): Prédiction par défaut si aucune détection n'est présente.
    
    Returns:
        dict: Dictionnaire contenant accuracy, precision, recall, f1 et un rapport détaillé.
    """
    y_true = []
    y_pred = []
    
    for cover, true_category in ground_truth.items():
        detections = logo_results.get(cover, {})
        if detections:
            votes = {}
            for detected_logo in detections.keys():
                # Chaque détection apporte une voix pour la catégorie correspondante
                category = logo_category_mapping.get(detected_logo, default_prediction)
                votes[category] = votes.get(category, 0) + 1
            # Sélectionner la catégorie avec le maximum de votes
            predicted_category = max(votes.items(), key=lambda x: x[1])[0]
        else:
            predicted_category = default_prediction
        
        y_true.append(true_category)
        y_pred.append(predicted_category)
    
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
        "f1": f1_score(y_true, y_pred, average='weighted', zero_division=0),
        "report": classification_report(y_true, y_pred, zero_division=0)
    }
    
    return metrics
