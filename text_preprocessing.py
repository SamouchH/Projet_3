# text_preprocessing.py
import re
import string

def clean_text(text):
    """
    Nettoie le texte en supprimant la ponctuation, en passant en minuscules et en éliminant les espaces superflus.
    
    Args:
        text (str): Texte brut
        
    Returns:
        str: Texte nettoyé
    """
    if not isinstance(text, str):
        return text
    # Convertir en minuscules
    text = text.lower()
    # Supprimer la ponctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text
