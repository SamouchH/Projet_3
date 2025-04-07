# data_loader.py
import os
import glob
import pandas as pd

def load_ocr_results(directory="ocr_results"):
    """
    Charge les fichiers CSV contenant les résultats OCR depuis le répertoire spécifié.
    
    Args:
        directory (str): Chemin du répertoire contenant les fichiers CSV
        
    Returns:
        dict: Dictionnaire de DataFrames avec le nom du filtre comme clé
    """
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans {directory}")
        return None
    
    print(f"{len(csv_files)} fichiers OCR trouvés")
    dfs = {}
    
    for csv_file in csv_files:
        try:
            # Extraction du nom du filtre depuis le nom du fichier
            filter_name = os.path.basename(csv_file).split('_', 2)[1]
            timestamp = '_'.join(os.path.basename(csv_file).split('_')[-2:]).replace('.csv', '')
            key = f"{filter_name}_{timestamp}"
            
            df = pd.read_csv(csv_file)
            
            # Vérification de la présence des colonnes nécessaires
            if 'extracted_text' not in df.columns:
                print(f"Avertissement : {csv_file} ne contient pas la colonne 'extracted_text', fichier ignoré")
                continue
            if 'filename' not in df.columns:
                print(f"Avertissement : {csv_file} ne contient pas la colonne 'filename', fichier ignoré")
                continue
            
            dfs[key] = df
            print(f"Chargé {os.path.basename(csv_file)} avec {len(df)} enregistrements")
            
        except Exception as e:
            print(f"Erreur lors du chargement de {csv_file} : {str(e)}")
    
    return dfs

def load_ground_truth(directory="data/batchs_csv"):
    """
    Charge les labels de référence à partir des fichiers CSV.
    
    Args:
        directory (str): Chemin du répertoire contenant les fichiers CSV de référence
        
    Returns:
        dict: Dictionnaire associant le nom de l'image à sa catégorie de plateforme
    """
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not csv_files:
        print(f"Aucun fichier de référence trouvé dans {directory}")
        return None
    
    print(f"{len(csv_files)} fichiers de référence trouvés")
    all_labels = {}
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            if 'image_name' in df.columns and 'category' in df.columns:
                category_mapping = {
                    'PC Gaming': 'pc',
                    'PC': 'pc',
                    'PlayStation': 'playstation',
                    'Xbox': 'xbox',
                    'Nintendo': 'nintendo',
                    'SEGA': 'sega'
                }
                
                df['platform'] = df['category'].apply(
                    lambda x: category_mapping.get(x, x.lower()) if isinstance(x, str) else "unknown"
                )
                
                for _, row in df.iterrows():
                    if 'image_name' in row and 'platform' in row:
                        all_labels[row['image_name']] = row['platform']
            else:
                print(f"Avertissement : Le fichier {csv_file} ne possède pas les colonnes attendues")
                
        except Exception as e:
            print(f"Erreur lors du chargement de {csv_file} : {str(e)}")
    
    print(f"{len(all_labels)} images étiquetées chargées")
    if all_labels:
        print("\nExemple de labels de référence :")
        for filename, platform in list(all_labels.items())[:5]:
            print(f"  {filename}: {platform}")
    
    return all_labels
