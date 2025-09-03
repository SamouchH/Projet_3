#!/usr/bin/env python3
"""
OCR Analyzer - A script to compare and evaluate different OCR preprocessing techniques
for detecting gaming platforms in images.

This script:
1. Loads OCR results from CSV files
2. Processes and corrects gaming platform references
3. Evaluates OCR performance using metrics (precision, recall, F1)
4. Visualizes the results and recommends the best preprocessing methods
"""

import os
import glob
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix
from improved_semantic_correction import advanced_semantic_correction
# Define gaming platforms and their variations
 # Define gaming platforms with common OCR variations and misspellings
GAMING_PLATFORMS = {
    "playstation": [
        "playstation", "playstaton", "playsation", "play station", "playstatlon", 
        "playstatidn", "pleystation", "plaustation", "playststion", "piaystation",
        "playstotion", "plsyst", "plsystn", "playstatn", "plstation", "playet",
        "ps4", "ps5", "ps3", "ps2", "ps1", "psx", "p54", "p55", "p53", "p52", "p51",
        "sony playstation", "sony play station", "play statian", "plehstatien"
    ],
    "xbox": [
        "xbox", "xbax", "x box", "x-box", "xboxx", "xbx", "xb0x", "xhox", "xdox",
        "xboc", "xboe", "xb", "xbex", "x b o x", "x-b-o-x", "x80x", "×box", "xhox",
        "xbox one", "xbox series", "xbox series x", "xbox series s", "microsoft xbox"
    ],
    "nintendo": [
        "nintendo", "nintondo", "nintend0", "nlntendo", "nlntend0", "nintenda", 
        "nitendo", "nintedo", "ninten", "nihtendo", "nintehdo", "nntendo", "nitend",
        "switch", "swtch", "swltch", "nintendo switch", "nintindo", "nintemdo",
        "wii", "wiiu", "wil", "wll", "nintendo wii", "wlio", "wlie", "wiii", "wi",
        "n64", "n-64", "n 64", "nlntendo 64", "nintendo64", "nintendo 64",
        "gamecube", "game cube", "game-cube", "nintendogamecube", "gome cube",
        "3ds", "2ds", "3 ds", "2 ds", "nintend0 3ds", "nintendo3ds", "nintendo 3ds"
    ],
    "pc": [
        "pc", "p c", "pc gaming", "personal computer", "desktop", "gaming pc", 
        "gaming p c", "windows", "win", "windowz", "p-c", "stearn", "steam",
        "computer", "laptop", "p.c.", "pc game", "p.c. game", "pc-game"
    ],
    "sega": [
        "sega", "saga", "sege", "segc", "sogo", "sego", "seg", "dreamcast", 
        "dream cast", "dream-cast", "dreamcost", "drecmcast", "dreomcast",
        "sega saturn", "saturn", "soturn", "sega genesis", "genesis", "mega drive",
        "megadrive", "mega-drive", "mego drive", "master system", "mastersystem"
    ]
}

def load_ocr_results(directory="ocr_results"):
    """
    Load OCR result files (CSV) from the specified directory.
    
    Args:
        directory (str): Path to directory containing OCR result CSV files
        
    Returns:
        dict: Dictionary of DataFrames with filter names as keys
    """
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {directory}")
        return None
    
    print(f"Found {len(csv_files)} OCR result files")
    
    # Create a dictionary to store dataframes
    dfs = {}
    
    for csv_file in csv_files:
        try:
            # Extract filter name from the filename
            # Example: ocr_adaptive_thresholding_20240307_123456.csv
            filter_name = os.path.basename(csv_file).split('_', 2)[1]
            
            # Add timestamp to distinguish multiple runs
            timestamp = '_'.join(os.path.basename(csv_file).split('_')[-2:]).replace('.csv', '')
            
            # Create a key for the dictionary
            key = f"{filter_name}_{timestamp}"
            
            # Load the CSV file
            df = pd.read_csv(csv_file)
            
            # Handle missing columns
            if 'extracted_text' not in df.columns:
                print(f"Warning: {csv_file} missing 'extracted_text' column, skipping")
                continue
                
            if 'filename' not in df.columns:
                print(f"Warning: {csv_file} missing 'filename' column, skipping")
                continue
            
            dfs[key] = df
            print(f"Loaded {os.path.basename(csv_file)} with {len(df)} records")
            
        except Exception as e:
            print(f"Error loading {csv_file}: {str(e)}")
    
    return dfs

def load_ground_truth(directory="data/batchs_csv"):
    """
    Load ground truth labels from CSV files.
    
    Args:
        directory (str): Path to directory containing ground truth CSV files
        
    Returns:
        dict: Dictionary mapping filenames to platform labels
    """
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not csv_files:
        print(f"No ground truth files found in {directory}")
        return None
    
    print(f"Found {len(csv_files)} ground truth files")
    
    # Create a dictionary to store all labels
    all_labels = {}
    
    for csv_file in csv_files:
        try:
            # Load the CSV file
            df = pd.read_csv(csv_file)
            
            # Check if it has the expected columns
            if 'image_name' in df.columns and 'category' in df.columns:
                # Standardize the platform naming
                category_mapping = {
                    'PC Gaming': 'pc',
                    'PC': 'pc',
                    'PlayStation': 'playstation',
                    'Xbox': 'xbox',
                    'Nintendo': 'nintendo',
                    'SEGA': 'sega'
                }
                
                # Apply mapping with fallback to lowercase
                df['platform'] = df['category'].apply(
                    lambda x: category_mapping.get(x, x.lower()) if isinstance(x, str) else "unknown"
                )
                
                # Add to the combined labels dictionary
                for _, row in df.iterrows():
                    if 'image_name' in row and 'platform' in row:
                        image_name = row['image_name']
                        platform = row['platform']
                        all_labels[image_name] = platform
            else:
                print(f"Warning: File {csv_file} does not have the expected columns")
                
        except Exception as e:
            print(f"Error loading {csv_file}: {str(e)}")
    
    print(f"Loaded {len(all_labels)} labeled images")
    
    # Print a sample of the ground truth labels
    if all_labels:
        print("\nSample of ground truth labels:")
        sample = list(all_labels.items())[:5]
        for filename, platform in sample:
            print(f"  {filename}: {platform}")
    
    return all_labels

def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein (edit) distance between two strings.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        
    Returns:
        int: Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
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

def find_closest_match(word, candidates, threshold=0.70):
    """
    Find the closest matching word from a list of candidates.
    
    Args:
        word (str): Word to find a match for
        candidates (list): List of candidate strings
        threshold (float): Similarity threshold (0-1)
        
    Returns:
        tuple: (best_match, similarity_score) or (None, 0) if no match found
    """
    word = word.lower()
    min_distance = float('inf')
    best_match = None
    
    for candidate in candidates:
        # Check exact match first
        if candidate == word:
            return candidate, 1.0
        
        # Calculate normalized edit distance (similarity score)
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



# def correct_platform_references(text):
#     """
#     Identify and correct gaming platform references in text using fuzzy matching.
    
#     Args:
#         text (str): Text to correct
        
#     Returns:
#         str: Text with corrected platform references
#     """
#     if pd.isna(text) or not isinstance(text, str):
#         return text
    
#     text = str(text).lower()
#     words = re.findall(r'\b\w+\b', text)
    
#     # Flatten all possible platform terms for initial matching
#     all_platform_terms = []
#     for platform_group in GAMING_PLATFORMS.values():
#         all_platform_terms.extend(platform_group)
    
#     corrections = {}
#     for word in words:
#         # Skip very short words
#         if len(word) < 3:
#             continue
            
#         closest_match, similarity = find_closest_match(word, all_platform_terms)
#         if closest_match:
#             # Find which platform category this belongs to
#             for platform, terms in GAMING_PLATFORMS.items():
#                 if closest_match in terms:
#                     # Store the mapping from original word to platform category
#                     corrections[word] = platform
#                     break
    
#     # Apply corrections
#     corrected_text = text
#     for original, correction in corrections.items():
#         # Use word boundaries to avoid partial replacements
#         corrected_text = re.sub(r'\b' + re.escape(original) + r'\b', correction, corrected_text)
    
#     return corrected_text



def extract_numbers(text):
    """
    Extract numerical values from text.
    
    Args:
        text (str): Text to extract numbers from
        
    Returns:
        list: List of extracted numbers
    """
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    # Regular expression to find numbers with optional decimal point
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    return [float(num) for num in numbers]

def test_semantic_correction():
    """
    Test the semantic correction function with sample OCR errors.
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
    
    print("Testing semantic correction functionality:")
    print("==========================================")
    for text in test_cases:
        corrected = advanced_semantic_correction(text)
        if text.lower() != corrected.lower():
            print(f"Original: {text}")
            print(f"Corrected: {corrected}")
            
            # Find what platform was detected
            platforms_found = []
            for platform in GAMING_PLATFORMS.keys():
                if platform in corrected.lower():
                    platforms_found.append(platform)
            
            print(f"Platform(s) detected: {', '.join(platforms_found)}")
            print("---")
        else:
            print(f"No correction needed: {text}")
            print("---")
    print()

def analyze_ocr_results(dfs, ground_truth_labels=None):
    """
    Analyze OCR results and evaluate performance.
    
    Args:
        dfs (dict): Dictionary of DataFrames with filter names as keys
        ground_truth_labels (dict, optional): Ground truth labels
        
    Returns:
        pd.DataFrame: Results summary
    """
    if not dfs:
        print("No OCR results to analyze")
        return None
    
    # Results dictionary
    results = {}
    
    for filter_name, df in dfs.items():
        # Skip if DataFrame is empty
        if df.empty:
            continue
        
        # Clean filter name for display
        clean_filter_name = filter_name.split('_')[0]
        
        # Apply semantic correction to text
        df['corrected_text'] = df['extracted_text'].apply(advanced_semantic_correction)
        
        # Check for gaming platforms in original and corrected text
        df['has_platform_original'] = df['extracted_text'].apply(
            lambda x: any(platform in str(x).lower() for platform in GAMING_PLATFORMS.keys()) 
            if not pd.isna(x) else False
        )
        df['has_platform_corrected'] = df['corrected_text'].apply(
            lambda x: any(platform in str(x).lower() for platform in GAMING_PLATFORMS.keys()) 
            if not pd.isna(x) else False
        )
        
        # Count platforms detected before and after correction
        platform_count_original = df['has_platform_original'].sum()
        platform_count_corrected = df['has_platform_corrected'].sum()
        platform_improvement = platform_count_corrected - platform_count_original
        
        # Extract numbers from text
        df['extracted_numbers'] = df['extracted_text'].apply(extract_numbers)
        df['number_count'] = df['extracted_numbers'].apply(len)
        total_numbers = df['number_count'].sum()
        
        # Calculate text length metrics
        df['text_length'] = df['extracted_text'].apply(
            lambda x: len(str(x)) if not pd.isna(x) else 0
        )
        avg_text_length = df['text_length'].mean()
        
        # Add processing time if available
        avg_processing_time = df['processing_time'].mean() if 'processing_time' in df.columns else np.nan
        
        # Initialize results dictionary for this filter
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
        
        # Add platform-specific counts
        for platform in GAMING_PLATFORMS.keys():
            platform_count = df['corrected_text'].apply(
                lambda x: platform in str(x).lower() if not pd.isna(x) else False
            ).sum()
            results[clean_filter_name][f'platform_{platform}'] = platform_count
        
        # If ground truth labels are available, calculate evaluation metrics
        if ground_truth_labels:
            metrics = calculate_metrics(df, ground_truth_labels)
            results[clean_filter_name].update({
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1': metrics['f1'],
                'evaluated_images': metrics['evaluated_images']
            })
            
            print(f"Metrics for {clean_filter_name}:")
            print(f"  F1: {metrics['f1']:.4f}, Precision: {metrics['precision']:.4f}, Recall: {metrics['recall']:.4f}")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  Evaluated on {metrics['evaluated_images']} images")
            print()
    
    # Convert to DataFrame for easier analysis
    results_df = pd.DataFrame(results).T
    
    # Sort by appropriate metric
    if ground_truth_labels and 'f1' in results_df.columns:
        # If we have evaluation metrics, sort by F1 score
        results_df = results_df.sort_values('f1', ascending=False)
    else:
        # Otherwise sort by platform detection rate
        results_df = results_df.sort_values('platform_count', ascending=False)
    
    return results_df

def calculate_metrics(df, ground_truth_labels):
    """
    Calculate evaluation metrics for platform detection.
    
    Args:
        df (pd.DataFrame): DataFrame with OCR results
        ground_truth_labels (dict): Ground truth platform labels
        
    Returns:
        dict: Dictionary of metrics
    """
    # Ensure corrected text is available
    if 'corrected_text' not in df.columns:
        df['corrected_text'] = df['extracted_text'].apply(advanced_semantic_correction)
    
    # Create a new column with predicted platform labels
    df['predicted_platform'] = 'unknown'
    
    # For each row, determine which platform(s) were detected
    for idx, row in df.iterrows():
        if not pd.isna(row['corrected_text']) and isinstance(row['corrected_text'], str):
            text = row['corrected_text'].lower()
            
            detected_platforms = []
            for platform in GAMING_PLATFORMS.keys():
                if platform in text:
                    detected_platforms.append(platform)
            
            if detected_platforms:
                # If multiple platforms detected, take the first one
                df.loc[idx, 'predicted_platform'] = detected_platforms[0]
    
    # Prepare for evaluation
    evaluation_data = []
    
    for _, row in df.iterrows():
        filename = row['filename']
        
        # Extract just the filename if it contains path information
        if '/' in filename or '\\' in filename:
            filename = os.path.basename(filename)
        
        predicted = row['predicted_platform']
        
        # Check if this image has ground truth
        if filename in ground_truth_labels:
            true_label = ground_truth_labels[filename]
            evaluation_data.append({
                'filename': filename,
                'true_label': true_label,
                'predicted': predicted,
                'correct': predicted == true_label
            })
    
    # If no evaluation data, return empty metrics
    if not evaluation_data:
        return {
            'accuracy': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0,
            'evaluated_images': 0
        }
    
    # Convert to DataFrame for easier analysis
    eval_df = pd.DataFrame(evaluation_data)
    
    # Calculate metrics
    y_true = eval_df['true_label'].values
    y_pred = eval_df['predicted'].values
    
    try:
        # Calculate precision, recall, f1
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        # Calculate accuracy
        accuracy = accuracy_score(y_true, y_pred)
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        precision, recall, f1, accuracy = 0, 0, 0, 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'evaluated_images': len(eval_df)
    }

def visualize_results(results_df, output_dir="plots"):
    """
    Create visualizations of the OCR results.
    
    Args:
        results_df (pd.DataFrame): Results summary DataFrame
        output_dir (str): Directory to save plots
    """
    if results_df is None or results_df.empty:
        print("No results to visualize")
        return
        
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up plot style
    plt.style.use('ggplot')
    sns.set(font_scale=1.2)
    
    # 1. Platform detection rate
    plt.figure(figsize=(12, 8))
    ax = results_df['platform_percentage'].sort_values(ascending=False).plot(kind='bar')
    ax.set_title('Platform Detection Rate by Preprocessing Filter')
    ax.set_ylabel('Detection Rate (%)')
    ax.set_xlabel('Preprocessing Filter')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_platform_detection_rate.png'))
    
    # 2. Original vs Corrected detection
    if 'platform_count_original' in results_df.columns:
        plt.figure(figsize=(14, 8))
        
        # Create a grouped bar chart
        width = 0.35
        x = np.arange(len(results_df.index))
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width/2, results_df['platform_count_original'], width, label='Original Text')
        ax.bar(x + width/2, results_df['platform_count'], width, label='With Semantic Correction')
        
        ax.set_title('Number of Images with Gaming Platform References Detected')
        ax.set_ylabel('Count')
        ax.set_xlabel('Preprocessing Filter')
        ax.set_xticks(x)
        ax.set_xticklabels(results_df.index, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '2_original_vs_corrected.png'))
    
    # 3. Platform breakdown
    platform_cols = [col for col in results_df.columns if col.startswith('platform_') 
                    and col not in ['platform_count', 'platform_count_original', 
                                   'platform_improvement', 'platform_percentage']]
    
    if platform_cols:
        # Create a stacked bar chart for top filters
        top_filters = results_df.head(10)
        platform_data = top_filters[platform_cols]
        
        # Rename columns for display
        platform_data.columns = [col.replace('platform_', '') for col in platform_data.columns]
        
        plt.figure(figsize=(14, 8))
        platform_data.plot(kind='bar', stacked=True, colormap='viridis')
        plt.title('Breakdown of Gaming Platform Types Detected by Top Filters')
        plt.ylabel('Count')
        plt.xlabel('Preprocessing Filter')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Platform Type')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '3_platform_breakdown.png'))
    
    # 4. Text length comparison
    plt.figure(figsize=(14, 8))
    ax = results_df['avg_text_length'].plot(kind='bar', color='purple')
    ax.set_title('Average Length of Extracted Text')
    ax.set_ylabel('Average Character Count')
    ax.set_xlabel('Preprocessing Filter')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '4_text_length.png'))
    
    # 5. Number extraction comparison
    plt.figure(figsize=(14, 8))
    ax = results_df['avg_numbers_per_image'].plot(kind='bar', color='green')
    ax.set_title('Average Number of Numerical Values Detected per Image')
    ax.set_ylabel('Average Count')
    ax.set_xlabel('Preprocessing Filter')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_number_extraction.png'))
    
    # 6. Processing time comparison (if available)
    if 'avg_processing_time' in results_df.columns and not results_df['avg_processing_time'].isna().all():
        plt.figure(figsize=(14, 8))
        ax = results_df['avg_processing_time'].plot(kind='bar', color='orange')
        ax.set_title('Average Processing Time per Image')
        ax.set_ylabel('Time (seconds)')
        ax.set_xlabel('Preprocessing Filter')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '6_processing_time.png'))
    
    # 7. Evaluation metrics (if available)
    if all(col in results_df.columns for col in ['precision', 'recall', 'f1', 'accuracy']):
        plt.figure(figsize=(14, 8))
        metrics_df = results_df[['precision', 'recall', 'f1', 'accuracy']].sort_values('f1', ascending=False).head(10)
        metrics_df.plot(kind='bar')
        plt.title('Evaluation Metrics by Filter')
        plt.ylabel('Score')
        plt.xlabel('Preprocessing Filter')
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '7_evaluation_metrics.png'))
        
        # 8. F1 Score Comparison
        plt.figure(figsize=(14, 8))
        top_10 = results_df.sort_values('f1', ascending=False).head(10)
        ax = top_10['f1'].plot(kind='bar', color='green')
        ax.set_title('F1 Score by Preprocessing Filter (Top 10)')
        ax.set_ylabel('F1 Score')
        ax.set_xlabel('Preprocessing Filter')
        plt.ylim(0, 1.0)
        for i, v in enumerate(top_10['f1']):
            ax.text(i, v + 0.02, f'{v:.2f}', ha='center')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '8_f1_comparison.png'))
    
    print(f"Saved {len(os.listdir(output_dir))} plots to {output_dir}")

def recommend_filters(results_df):
    """
    Recommend the best preprocessing filters based on evaluation results.
    
    Args:
        results_df (pd.DataFrame): Results summary DataFrame
    """
    if results_df is None or results_df.empty:
        print("No results for recommendations")
        return
    
    print("\nBest Filters Recommendation:")
    print("============================")
    
    # Check if we have evaluation metrics
    has_metrics = all(col in results_df.columns for col in ['precision', 'recall', 'f1'])
    
    # Create a comprehensive score
    if has_metrics:
        # Score based primarily on F1 score, with secondary factors
        results_df['score'] = (
            0.6 * results_df['f1'] + 
            0.2 * results_df['precision'] + 
            0.2 * results_df['recall']
        )
        results_df = results_df.sort_values('score', ascending=False)
        
        print("\nTop 5 filters based on F1 score:")
    else:
        # Fallback scoring based on platform detection
        results_df['score'] = (
            0.5 * (results_df['platform_percentage'] / results_df['platform_percentage'].max()) + 
            0.3 * (results_df['total_numbers'] / results_df['total_numbers'].max() if results_df['total_numbers'].max() > 0 else 0) + 
            0.2 * (results_df['avg_text_length'] / results_df['avg_text_length'].max() if results_df['avg_text_length'].max() > 0 else 0)
        )
        results_df = results_df.sort_values('score', ascending=False)
        
        print("\nTop 5 filters based on platform detection:")
    
    # Display top 5 filters
    for i, (filter_name, row) in enumerate(results_df.head(5).iterrows()):
        print(f"{i+1}. {filter_name} (Score: {row['score']:.2f})")
        
        if has_metrics:
            print(f"   - F1 Score: {row['f1']:.3f}")
            print(f"   - Precision: {row['precision']:.3f}")
            print(f"   - Recall: {row['recall']:.3f}")
            print(f"   - Accuracy: {row['accuracy']:.3f}")
            print(f"   - Evaluated on: {row['evaluated_images']} labeled images")
        
        print(f"   - Gaming platforms detected: {row['platform_count']} ({row['platform_percentage']:.1f}%)")
        print(f"   - Numbers extracted: {row['total_numbers']} (avg {row['avg_numbers_per_image']:.1f} per image)")
        print(f"   - Average text length: {row['avg_text_length']:.1f} characters")
        
        if 'avg_processing_time' in row and not pd.isna(row['avg_processing_time']):
            print(f"   - Average processing time: {row['avg_processing_time']:.2f} seconds")
        print()
    
    # Final recommendation
    best_filter = results_df.index[0]
    print("\nFinal Recommendation:")
    if has_metrics:
        print(f"The best preprocessing approach based on F1 score is: {best_filter}")
    else:
        print(f"The best preprocessing approach appears to be: {best_filter}")

def main():
    """Main function to run the OCR analysis"""
    print("OCR Analyzer - Comparing preprocessing techniques for OCR")
    print("========================================================")
    
    # Test the semantic correction function
    test_semantic_correction()
    
    # Set directories
    ocr_dir = "ocr_results"  # Directory with OCR result CSV files
    gt_dir = "data/batchs_csv"  # Directory with ground truth label CSV files
    plots_dir = "plots"  # Directory to save plots
    
    # Load ground truth labels
    print("\nLoading ground truth labels...")
    ground_truth = load_ground_truth(gt_dir)
    
    # Load OCR results
    print("\nLoading OCR results...")
    ocr_results = load_ocr_results(ocr_dir)
    
    if not ocr_results:
        print("No OCR results to analyze. Exiting.")
        return
    
    # Analyze results
    print("\nAnalyzing OCR results...")
    if ground_truth:
        print(f"Using ground truth for {len(ground_truth)} labeled images")
        results = analyze_ocr_results(ocr_results, ground_truth)
    else:
        print("No ground truth labels found. Analyzing without evaluation metrics.")
        results = analyze_ocr_results(ocr_results)
    
    if results is not None:
        # Display results summary
        print("\nResults Summary:")
        print("===============")
        print(results)
        
        # Create visualizations
        print("\nCreating visualizations...")
        visualize_results(results, plots_dir)
        
        # Recommend filters
        recommend_filters(results)
    else:
        print("Analysis failed to produce results.")
    
    print("\nDone!")
    print("========================================================")       


    # Run the analysis
if __name__ == "__main__":
    main()