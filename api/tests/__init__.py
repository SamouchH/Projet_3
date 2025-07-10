# Tests pour l'API Projet_3

import os
import sys
from pathlib import Path

# Ajout du répertoire racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root)) 