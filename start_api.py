#!/usr/bin/env python3
"""
Script de démarrage de l'API Projet_3

Ce script configure et démarre l'API avec toutes ses dépendances.
Il vérifie la configuration, prépare l'environnement et lance le serveur.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional

def print_banner():
    """Affichage de la bannière de démarrage"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                        🎮 PROJET_3 API                      ║  
║                                                              ║
║  API de Classification d'Images de Jeux Vidéo                ║
║  Version: 1.0.0                                              ║
║                                                              ║
║  Fonctionnalités:                                            ║
║  • 🔐 Authentification JWT sécurisée                        ║
║  • 🎯 Classification automatique d'images                   ║
║  • 📊 Dashboard d'administration                            ║
║  • 🛡️ Sécurité et rate limiting                              ║
║  • 📈 Monitoring et métriques                               ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Vérification des prérequis"""
    print("🔍 Vérification des prérequis...")
    
    # Vérification de Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    
    # Vérification du modèle ML
    model_paths = [
        "modele_cnn_transfer.h5",
        "Streamlit/modele_cnn_transfer.h5",
        "../Streamlit/modele_cnn_transfer.h5"
    ]
    
    model_found = False
    for path in model_paths:
        if Path(path).exists():
            print(f"✅ Modèle trouvé : {path}")
            # Créer un lien symbolique vers l'API si nécessaire
            api_model_path = Path("api/modele_cnn_transfer.h5")
            if not api_model_path.exists():
                try:
                    os.symlink(os.path.abspath(path), api_model_path)
                    print(f"🔗 Lien créé vers le modèle")
                except:
                    import shutil
                    shutil.copy2(path, api_model_path)
                    print(f"📋 Modèle copié")
            model_found = True
            break
    
    if not model_found:
        print("❌ Modèle ML non trouvé. Assurez-vous que 'modele_cnn_transfer.h5' existe.")
        return False
    
    print("✅ Prérequis validés")
    return True

def setup_environment():
    """Configuration de l'environnement"""
    print("⚙️  Configuration de l'environnement...")
    
    # Création des répertoires nécessaires
    directories = [
        "api/logs",
        "api/uploads", 
        "api/predictions",
        "api/data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Configuration des variables d'environnement par défaut
    env_vars = {
        "PYTHONPATH": str(Path.cwd()),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("✅ Environnement configuré")

def install_dependencies():
    """Installation des dépendances"""
    print("📦 Vérification des dépendances...")
    
    requirements_file = Path("api/requirements.txt")
    if not requirements_file.exists():
        print("❌ Fichier requirements.txt non trouvé")
        return False
    
    try:
        # Vérification si les packages sont installés
        result = subprocess.run([
            sys.executable, "-m", "pip", "check"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("🔄 Installation des dépendances...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Dépendances installées")
        else:
            print("✅ Dépendances déjà installées")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation : {e}")
        return False

def start_api_server(host: str = "0.0.0.0", port: int = 8080, reload: bool = False):
    """Démarrage du serveur API"""
    print(f"🚀 Démarrage du serveur API sur {host}:{port}...")
    
    # Import et configuration de l'API
    sys.path.insert(0, str(Path.cwd()))
    
    try:
        # Commande uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", host,
            "--port", str(port),
            "--log-level", os.getenv("LOG_LEVEL", "info").lower()
        ]
        
        if reload:
            cmd.append("--reload")
        
        # Variables d'environnement pour le processus
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd())
        
        # Démarrage du serveur
        process = subprocess.Popen(cmd, env=env)
        
        # Gestionnaire de signal pour arrêt propre
        def signal_handler(sig, frame):
            print("\n🛑 Arrêt du serveur...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Attente du processus
        print(f"✅ Serveur démarré avec succès!")
        print(f"📖 Documentation : http://{host}:{port}/docs")
        print(f"🔄 API Health Check : http://{host}:{port}/health")
        print(f"👤 Utilisateurs par défaut :")
        print(f"   Admin: admin / admin123!")
        print(f"   User:  testuser / user123!")
        print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
        
        process.wait()
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage : {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print_banner()
    
    # Arguments de ligne de commande basiques
    import argparse
    parser = argparse.ArgumentParser(description="Démarrage de l'API Projet_3")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=8080, help="Port d'écoute")
    parser.add_argument("--reload", action="store_true", help="Mode rechargement automatique")
    parser.add_argument("--skip-deps", action="store_true", help="Ignorer l'installation des dépendances")
    
    args = parser.parse_args()
    
    # Vérifications et configuration
    if not check_requirements():
        sys.exit(1)
    
    setup_environment()
    
    if not args.skip_deps and not install_dependencies():
        sys.exit(1)
    
    # Démarrage du serveur
    if not start_api_server(args.host, args.port, args.reload):
        sys.exit(1)

if __name__ == "__main__":
    main() 