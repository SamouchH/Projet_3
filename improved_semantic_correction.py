# Import specialized libraries directly
from jellyfish import jaro_winkler_similarity
from fuzzywuzzy import fuzz
import pandas as pd
import string
import re

# Import les variables globales depuis global.py
from global_config import (
    GAMING_PLATFORMS, 
    ALL_PLATFORM_TERMS, 
    PLATFORM_TERM_CATEGORY, 
    CONTEXT_MARKERS, 
    HIGH_CONFIDENCE_INDICATORS, 
    DEFAULT_WEIGHTS, 
    SHORT_QUERY_WEIGHTS, 
    COMMON_ABBREVIATIONS
)

# ------------------------
# Similarity Functions
# ------------------------

def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein (edit) distance between two strings.
    Optimized version with early exits and matrix optimization.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        
    Returns:
        int: Edit distance (lower is more similar)
    """
    # Early exits for empty strings
    if not s1: return len(s2)
    if not s2: return len(s1)
    
    # Early exit for strings that are too different in length
    if abs(len(s1) - len(s2)) > min(len(s1), len(s2)):
        return max(len(s1), len(s2))
    
    # Early exit for identical strings
    if s1 == s2:
        return 0
    
    # Make s1 the shorter string for optimization
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    
    # Use list comprehension for better performance in matrix creation
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Calculate insertions, deletions and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def levenshtein_similarity(s1, s2):
    """
    Calculate normalized Levenshtein similarity between two strings.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        
    Returns:
        float: Similarity score between 0 and 1 (higher is more similar)
    """
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0  # Both strings are empty
    return 1.0 - (distance / max_len)

def character_ngram_similarity(s1, s2, n=2):
    """
    Calculate character-level n-gram similarity between two strings.
    Uses Jaccard similarity on character n-grams.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        n (int): Size of n-grams
        
    Returns:
        float: Similarity score between 0 and 1 (higher is more similar)
    """
    if not s1 or not s2:
        return 0.0
    
    # Quick exit for very different length strings
    if abs(len(s1) - len(s2)) / max(len(s1), len(s2)) > 0.5:
        return 0.0
    
    # Handle cases where strings are too short for n-grams
    if len(s1) < n or len(s2) < n:
        return levenshtein_similarity(s1, s2)
    
    # Generate character n-grams and convert directly to sets for efficiency
    ngrams1 = {s1[i:i+n] for i in range(len(s1) - n + 1)}
    ngrams2 = {s2[i:i+n] for i in range(len(s2) - n + 1)}
    
    # Calculate Jaccard similarity
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    
    return intersection / union if union > 0 else 0.0



def fuzzy_similarity(s1, s2):
    """
    Calculate fuzzy similarity between two strings.
    Uses fuzzywuzzy's token sort ratio.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        
    Returns:
        float: Similarity score between 0 and 1 (higher is more similar)
    """
    return fuzz.token_sort_ratio(s1, s2) / 100.0

def multi_metric_match(query, candidates=None, min_threshold=0.65):
    """
    Find the best match using multiple similarity metrics with weighted voting.
    Optimized for performance.
    
    Args:
        query (str): String to find matches for
        candidates (list, optional): List of candidate strings to match against. 
                                    If None, uses global ALL_PLATFORM_TERMS.
        min_threshold (float): Minimum similarity threshold to consider a match valid
        
    Returns:
        tuple: (best_match, confidence_score, metrics_scores)
    """
    # Use provided candidates or default to global ALL_PLATFORM_TERMS
    if candidates is None:
        candidates = ALL_PLATFORM_TERMS
    # Skip very short queries unless they're common platform abbreviations
    if len(query) <= 2 and query not in COMMON_ABBREVIATIONS:
        return None, 0.0, {}
    
    # Check for exact match first
    for candidate in candidates:
        if query == candidate:
            return candidate, 1.0, {'exact': 1.0}
    
    # Weights for different metrics - use global weights
    weights = DEFAULT_WEIGHTS.copy() 
    # Remove phonetic weight since we're not using it anymore
    if 'phonetic' in weights:
        del weights['phonetic']
        # Redistribute the weights
        weights['levenshtein'] += 0.05
        weights['jaro_winkler'] += 0.05
        weights['fuzzy'] += 0.05
    
    best_match = None
    best_score = 0.0
    metrics_scores = {}
    
    # Dynamically adjust threshold based on query length
    threshold = min_threshold
    if len(query) <= 3:
        threshold = 0.75  # Higher threshold for very short strings
    elif len(query) <= 5:
        threshold = 0.70  # Slightly higher threshold for short strings
    
    # Well-known abbreviations get a lower threshold
    if query in COMMON_ABBREVIATIONS:
        threshold = 0.60
        
    # Special weighting for very short queries
    if len(query) <= 3:
        # Use global SHORT_QUERY_WEIGHTS and remove phonetic if present
        weights = SHORT_QUERY_WEIGHTS.copy()
        if 'phonetic' in weights:
            del weights['phonetic']
            # Redistribute the weights
            weights['levenshtein'] += 0.05
            weights['jaro_winkler'] += 0.05
    
    for candidate in candidates:
        # Skip candidates that are too different in length
        if abs(len(query) - len(candidate)) > max(3, min(len(query), len(candidate)) // 2):
            continue
        
        # Calculate similarity using different metrics
        lev_sim = levenshtein_similarity(query, candidate)
        jaro_sim = jaro_winkler_similarity(query, candidate)
        ngram_sim = character_ngram_similarity(query, candidate)
        fuzz_sim = fuzzy_similarity(query, candidate)
        
        # Weight the scores
        combined_score = (
            weights['levenshtein'] * lev_sim +
            weights['jaro_winkler'] * jaro_sim +
            weights['char_ngram'] * ngram_sim +
            weights['fuzzy'] * fuzz_sim
        )
        
        # Bonus for prefix matches
        if candidate.startswith(query) or query.startswith(candidate):
            min_len = min(len(query), len(candidate))
            max_len = max(len(query), len(candidate))
            prefix_bonus = (min_len / max_len) * 0.1
            combined_score += prefix_bonus
        
        # Store if this is the best match so far
        if combined_score > best_score:
            best_match = candidate
            best_score = combined_score
            metrics_scores = {
                'levenshtein': lev_sim,
                'jaro_winkler': jaro_sim,
                'char_ngram': ngram_sim,
                'fuzzy': fuzz_sim,
                'combined': combined_score
            }
    
    # Only return match if it exceeds threshold
    if best_score >= threshold:
        return best_match, best_score, metrics_scores
    return None, 0.0, {}

def advanced_semantic_correction(text):
    """
    Advanced function to detect gaming platforms in OCR text using multiple
    similarity metrics and machine learning techniques.
    
    This optimized version uses:
    1. Multiple similarity metrics (Levenshtein, Jaro-Winkler, etc.)
    2. Weighted voting approach for multiple metrics
    3. Character-level n-gram comparison
    4. Context-dependent similarity thresholds
    
    Args:
        text (str): Text to analyze and correct
        
    Returns:
        str: Text with corrected platform references
    """
    global GAMING_PLATFORMS
    # Return original text if input is not valid
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    # Convert to lowercase and remove excess whitespace
    text = str(text).lower().strip()
    cleaned_text = ' '.join(text.split())
    
    # Pre-processing: replace hyphens, underscores, etc. with spaces for better tokenization
    for char in ['-', '_', '.', ',', '/', '\\', '|', ':', ';', '(', ')', '[', ']', '{', '}']:
        cleaned_text = cleaned_text.replace(char, ' ')
    
    # Remove punctuation except spaces and make sure we have no double spaces
    cleaned_text = ''.join([c for c in cleaned_text if c not in string.punctuation or c == ' '])
    cleaned_text = ' '.join(cleaned_text.split())
    
    # Extract words and create n-grams
    words = cleaned_text.split()
    
    # Generate n-grams (1-3)
    unigrams = words
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words) - 1)]
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]
    
    # All n-grams
    all_ngrams = unigrams + bigrams + trigrams
    
    # Generate a list of all platform terms
    # We're using global ALL_PLATFORM_TERMS and PLATFORM_TERM_CATEGORY 
    # instead of recreating them
    
    # Process all n-grams to find platform matches
    corrections = {}
    detected_platforms = set()
    
    # Common gaming context markers that can help identify platform references
    # Use global CONTEXT_MARKERS
    
    # Check if we have gaming context in the text
    has_context = any(marker in cleaned_text for marker in CONTEXT_MARKERS)
    
    # Process n-grams from longest to shortest
    for ngram in trigrams + bigrams + unigrams:
        # Skip if too short (except common abbreviations)
        if len(ngram) < 2 and ngram not in ['pc', 'ps']:
            continue
        
        # Adjust threshold based on context
        threshold = 0.65  # Default threshold
        if has_context:
            threshold = 0.60  # Lower threshold if gaming context is present
        
        # Find best match across all metrics
        best_match, confidence, metrics = multi_metric_match(ngram, ALL_PLATFORM_TERMS, threshold)
        
        if best_match and confidence > 0:
            platform = PLATFORM_TERM_CATEGORY[best_match]
            
            # Skip if we already detected this platform from a longer ngram
            if platform in detected_platforms and ngram in unigrams and len(detected_platforms) > 1:
                continue
                
            corrections[ngram] = platform
            detected_platforms.add(platform)
    
    # Apply corrections in order of ngram length (longest first)
    sorted_corrections = sorted(corrections.items(), key=lambda x: len(x[0]), reverse=True)
    corrected_text = cleaned_text
    
    for original, correction in sorted_corrections:
        # Use word boundaries to avoid partial replacements
        pattern = r'\b' + re.escape(original) + r'\b'
        corrected_text = re.sub(pattern, correction, corrected_text)
    
    # Post-processing: Check for high-confidence platform markers we might have missed
    # Use global HIGH_CONFIDENCE_INDICATORS
    
    # Check for specific platform indicators and add if missing
    for platform, indicators in HIGH_CONFIDENCE_INDICATORS.items():
        if platform not in corrected_text:  # Only if not already detected
            for indicator in indicators:
                if indicator in cleaned_text:
                    # Append the platform name at the end
                    corrected_text += f" {platform}"
                    break
    
    return corrected_text