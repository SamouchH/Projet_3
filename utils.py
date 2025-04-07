# utils.py
import re
import pandas as pd

def levenshtein_distance(s1, s2):
    """
    Calcule la distance de Levenshtein entre deux chaînes.
    
    Args:
        s1 (str): Première chaîne
        s2 (str): Deuxième chaîne
        
    Returns:
        int: Distance d'édition
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def find_closest_match(word, candidates, threshold=0.70):
    """
    Trouve la correspondance la plus proche dans une liste de candidats.
    
    Args:
        word (str): Mot à comparer
        candidates (list): Liste de chaînes candidates
        threshold (float): Seuil de similarité (0-1)
        
    Returns:
        tuple: (meilleur_match, score_de_similarité) ou (None, 0) si aucun match n'est trouvé
    """
    word = word.lower()
    min_distance = float('inf')
    best_match = None
    
    for candidate in candidates:
        if candidate == word:
            return candidate, 1.0
        
        max_len = max(len(word), len(candidate))
        if max_len == 0:
            continue
            
        distance = levenshtein_distance(word, candidate)
        similarity = 1 - (distance / max_len)
        
        if similarity > threshold and similarity > (1 - min_distance / max_len):
            min_distance = distance
            best_match = candidate
    
    if best_match:
        return best_match, 1 - (min_distance / max(len(word), len(best_match)))
    return None, 0

def extract_numbers(text):
    """
    Extrait les valeurs numériques d'un texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        list: Liste de nombres extraits
    """
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    return [float(num) for num in numbers]
