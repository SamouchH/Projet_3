# vectorizers.py
from sklearn.feature_extraction.text import TfidfVectorizer

def get_tfidf_vectorizer(ngram_range=(1,2), max_features=2000, stop_words='english'):
    """
    Crée et renvoie un TfidfVectorizer configuré.
    
    Args:
        ngram_range (tuple): Plage d'n‑grammes à utiliser
        max_features (int): Nombre maximal de caractéristiques
        stop_words (str): Stop words à utiliser
    
    Returns:
        TfidfVectorizer: Instance configurée
    """
    vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features, stop_words=stop_words)
    return vectorizer

def get_transformer_embeddings(texts, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Utilise un modèle pré-entraîné pour obtenir des embeddings de texte.
    
    Args:
        texts (list of str): Liste de textes
        model_name (str): Nom du modèle pré-entraîné
        
    Returns:
        np.array: Matrice d'embeddings
    """
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts)
    return embeddings
