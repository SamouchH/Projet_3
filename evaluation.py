# evaluation.py
from sklearn.metrics import classification_report, accuracy_score

def evaluate_classical_model(model, X_test, y_test):
    """
    Évalue un modèle classique en affichant le rapport de classification.
    
    Args:
        model: Pipeline entraînée
        X_test: Jeu de test (texte)
        y_test: Labels du jeu de test
    """
    y_pred = model.predict(X_test)
    print("=== Rapport de classification ===")
    print(classification_report(y_test, y_pred))
    print("Accuracy :", accuracy_score(y_test, y_pred))
