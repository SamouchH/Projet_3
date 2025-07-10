#!/bin/bash

# Script de lancement rapide de l'API Projet_3
# Usage: ./launch_api.sh [options]

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction d'affichage de bannière
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        🎮 PROJET_3 API                      ║"  
    echo "║                                                              ║"
    echo "║  API de Classification d'Images de Jeux Vidéo               ║"
    echo "║  Version: 1.0.0                                             ║"
    echo "║                                                              ║"
    echo "║  🔐 Authentification JWT  📊 Admin Dashboard                ║"
    echo "║  🎯 Classification ML     🛡️ Sécurité avancée               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Afficher cette aide"
    echo "  -p, --port PORT     Port d'écoute (défaut: 8080)"
    echo "  -r, --reload        Mode rechargement automatique"
    echo "  -d, --docker        Lancer avec Docker"
    echo "  -t, --test          Lancer les tests"
    echo "  --install           Installer les dépendances uniquement"
    echo "  --clean             Nettoyer les fichiers temporaires"
    echo ""
    echo "Exemples:"
    echo "  $0                  # Lancement normal"
    echo "  $0 -p 9000 -r       # Port 9000 avec rechargement"
    echo "  $0 -d               # Lancement avec Docker"
    echo "  $0 -t               # Exécution des tests"
}

# Variables par défaut
PORT=8080
RELOAD=false
DOCKER=false
TEST=false
INSTALL_ONLY=false
CLEAN=false

# Parse des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -r|--reload)
            RELOAD=true
            shift
            ;;
        -d|--docker)
            DOCKER=true
            shift
            ;;
        -t|--test)
            TEST=true
            shift
            ;;
        --install)
            INSTALL_ONLY=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            echo -e "${RED}❌ Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Fonction de nettoyage
clean_files() {
    echo -e "${YELLOW}🧹 Nettoyage des fichiers temporaires...${NC}"
    
    # Suppression des fichiers temporaires
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Suppression des logs et bases de données de test
    rm -f api/logs/*.log* 2>/dev/null || true
    rm -f *.db 2>/dev/null || true
    rm -f test_*.db 2>/dev/null || true
    
    echo -e "${GREEN}✅ Nettoyage terminé${NC}"
}

# Fonction de vérification des prérequis
check_requirements() {
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"
    
    # Vérification Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} détecté${NC}"
    
    # Vérification du modèle ML
    MODEL_PATHS=("modele_cnn_transfer.h5" "Streamlit/modele_cnn_transfer.h5" "../Streamlit/modele_cnn_transfer.h5")
    MODEL_FOUND=false
    
    for model_path in "${MODEL_PATHS[@]}"; do
        if [[ -f "$model_path" ]]; then
            echo -e "${GREEN}✅ Modèle trouvé : $model_path${NC}"
            # Créer un lien vers l'API si nécessaire
            if [[ ! -f "api/modele_cnn_transfer.h5" ]]; then
                mkdir -p api
                cp "$model_path" "api/modele_cnn_transfer.h5"
                echo -e "${CYAN}📋 Modèle copié vers l'API${NC}"
            fi
            MODEL_FOUND=true
            break
        fi
    done
    
    if [[ "$MODEL_FOUND" = false ]]; then
        echo -e "${RED}❌ Modèle ML non trouvé. Recherche de 'modele_cnn_transfer.h5'${NC}"
        exit 1
    fi
}

# Fonction d'installation des dépendances
install_dependencies() {
    echo -e "${BLUE}📦 Installation des dépendances...${NC}"
    
    # Vérifier si requirements.txt existe
    if [[ ! -f "api/requirements.txt" ]]; then
        echo -e "${RED}❌ Fichier requirements.txt non trouvé dans api/${NC}"
        exit 1
    fi
    
    # Installation avec pip
    if python3 -m pip install -r api/requirements.txt --quiet; then
        echo -e "${GREEN}✅ Dépendances installées avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
        exit 1
    fi
}

# Fonction de configuration de l'environnement
setup_environment() {
    echo -e "${BLUE}⚙️ Configuration de l'environnement...${NC}"
    
    # Création des répertoires
    mkdir -p api/{logs,uploads,predictions,data}
    
    # Variables d'environnement par défaut
    export PYTHONPATH="$(pwd)"
    export ENVIRONMENT="${ENVIRONMENT:-development}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    echo -e "${GREEN}✅ Environnement configuré${NC}"
}

# Fonction de lancement avec Docker
launch_docker() {
    echo -e "${BLUE}🐳 Lancement avec Docker...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker n'est pas installé${NC}"
        exit 1
    fi
    
    if [[ -f "api/docker-compose.yml" ]]; then
        echo -e "${CYAN}🚀 Démarrage avec Docker Compose...${NC}"
        cd api
        docker-compose up --build -d
        cd ..
        
        echo -e "${GREEN}✅ Services Docker démarrés !${NC}"
        echo -e "${CYAN}📖 API Documentation : http://localhost:8080/docs${NC}"
        echo -e "${CYAN}📊 Grafana : http://localhost:3000 (admin/admin)${NC}"
        echo -e "${CYAN}📈 Prometheus : http://localhost:9090${NC}"
    else
        echo -e "${YELLOW}⚠️ docker-compose.yml non trouvé, construction simple...${NC}"
        cd api
        docker build -t projet3-api .
        docker run -p ${PORT}:8080 -v "$(pwd)/../Streamlit/modele_cnn_transfer.h5:/app/modele_cnn_transfer.h5:ro" projet3-api
        cd ..
    fi
}

# Fonction de lancement normal
launch_normal() {
    echo -e "${BLUE}🚀 Démarrage du serveur API...${NC}"
    
    # Construction de la commande uvicorn
    CMD="python3 -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"
    
    if [[ "$RELOAD" = true ]]; then
        CMD="${CMD} --reload"
    fi
    
    echo -e "${CYAN}📡 Commande : ${CMD}${NC}"
    echo -e "${GREEN}✅ Serveur démarré sur http://localhost:${PORT}${NC}"
    echo -e "${CYAN}📖 Documentation : http://localhost:${PORT}/docs${NC}"
    echo -e "${CYAN}🔄 Health Check : http://localhost:${PORT}/health${NC}"
    echo ""
    echo -e "${YELLOW}👤 Utilisateurs par défaut :${NC}"
    echo -e "${CYAN}   Admin: admin / admin123!${NC}"
    echo -e "${CYAN}   User:  testuser / user123!${NC}"
    echo ""
    echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter le serveur${NC}"
    
    # Lancement du serveur
    exec $CMD
}

# Fonction de tests
run_tests() {
    echo -e "${BLUE}🧪 Exécution des tests...${NC}"
    
    if ! command -v pytest &> /dev/null; then
        echo -e "${YELLOW}⚠️ pytest non trouvé, installation...${NC}"
        python3 -m pip install pytest pytest-asyncio
    fi
    
    # Exécution des tests
    if python3 -m pytest api/tests/ -v --tb=short; then
        echo -e "${GREEN}✅ Tous les tests sont passés !${NC}"
    else
        echo -e "${RED}❌ Certains tests ont échoué${NC}"
        exit 1
    fi
}

# Fonction principale
main() {
    print_banner
    
    # Gestion des options spéciales
    if [[ "$CLEAN" = true ]]; then
        clean_files
        exit 0
    fi
    
    if [[ "$TEST" = true ]]; then
        check_requirements
        setup_environment
        install_dependencies
        run_tests
        exit 0
    fi
    
    # Vérifications et installation
    check_requirements
    setup_environment
    install_dependencies
    
    if [[ "$INSTALL_ONLY" = true ]]; then
        echo -e "${GREEN}✅ Installation terminée !${NC}"
        exit 0
    fi
    
    # Lancement
    if [[ "$DOCKER" = true ]]; then
        launch_docker
    else
        launch_normal
    fi
}

# Gestion des signaux pour arrêt propre
trap 'echo -e "\n${YELLOW}🛑 Arrêt en cours...${NC}"; exit 0' INT TERM

# Exécution
main "$@" 