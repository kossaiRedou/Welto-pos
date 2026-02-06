# -*- coding: utf-8 -*-
"""
Serveur Django pur avec Uvicorn pour DAMA Desktop
Usage: python Welto.py (serveur seulement, pas Electron)
"""

import sys
import os
import uvicorn

# Configuration PYTHONPATH pour PyInstaller
def setup_django_paths():
    """Configure les chemins Django pour PyInstaller"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Si on est dans un exécutable PyInstaller, utiliser le répertoire temporaire
    if getattr(sys, 'frozen', False):
        # Mode PyInstaller - utiliser le répertoire de l'exécutable
        bundle_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        django_dir = bundle_dir
    else:
        # Mode développement - utiliser le répertoire courant
        django_dir = current_dir
    
    # Ajouter au PYTHONPATH si pas déjà présent
    if django_dir not in sys.path:
        sys.path.insert(0, django_dir)
    
    # Configurer les variables d'environnement Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_pos.settings')
    
    return django_dir

def run_migrations():
    """
    Exécute automatiquement les migrations Django au démarrage
    """
    print("[DAMA] Verification des migrations de la base de donnees...")
    
    try:
        # Importer Django
        import django
        from django.core.management import call_command
        
        # Setup Django
        django.setup()
        
        # Exécuter les migrations
        print("[DAMA] Application des migrations...")
        call_command('migrate', '--noinput', verbosity=0)
        print("[DAMA] Migrations appliquees avec succes")
        
        return True
    except Exception as e:
        print(f"[DAMA] Erreur lors des migrations: {e}")
        print("[DAMA] Le serveur va demarrer mais la base peut etre incomplete")
        return False

def run_django_server():
    """
    Lance le serveur Django avec Uvicorn - SERVEUR PUR OPTIMISÉ
    Utilisé par Electron via main.js
    """
    # Exécuter les migrations avant de démarrer le serveur
    run_migrations()
    
    print("[DAMA] Demarrage du serveur Django (Uvicorn)...")
    print("[DAMA] Serveur disponible sur http://127.0.0.1:8000")
    print("[DAMA] Configuration haute performance activée")
    
    # Configuration Uvicorn ultra-optimisée pour desktop
    uvicorn.run(
        "blog_pos.asgi:application",
        host="127.0.0.1",
        port=8000,
        # Performance ultra-optimisée pour Windows
        workers=1,                      # 1 worker parfait pour desktop
        loop="asyncio",                 # asyncio natif Windows (uvloop non compatible)
        http="httptools",               # httptools pour HTTP rapide
        ws="websockets",                # WebSockets natifs
        lifespan="off",                 # Désactiver lifespan pour Django
        # Logging minimal pour vitesse
        log_level="error",              # Seulement les erreurs critiques
        access_log=False,               # Pas de logs d'accès
        use_colors=False,               # Désactiver les couleurs pour performance
        # Buffers et timeouts ultra-optimisés
        limit_concurrency=50,           # Réduit pour desktop
        limit_max_requests=2000,        # Augmenté pour éviter les redémarrages
        timeout_keep_alive=60,          # Keep-alive plus long
        timeout_graceful_shutdown=15,   # Arrêt plus propre
        backlog=512,                    # Buffer connexions
        # Production settings
        reload=False,                   # Pas de reload
        reload_dirs=[],                 # Pas de surveillance fichiers
        # Interface optimisée
        server_header=False,            # Pas de header serveur
        date_header=False,              # Pas de header date
        # Stabilité maximale
        factory=False,                  # Pas de factory pattern
        proxy_headers=False,            # Pas de proxy headers
    )

if __name__ == "__main__":
    print("=" * 60)
    print("[DAMA] Django Server - Mode Standalone")
    print("=" * 60)
    print("[INFO] Usage:")
    print("  - Serveur seul: python Welto.py")
    print("  - App Desktop:  cd ../desktop_app && npm start")
    print("=" * 60)
    
    # Configuration des chemins Django pour PyInstaller
    django_path = setup_django_paths()
    print(f"[DAMA] Chemin Django configuré: {django_path}")
    
    try:
        run_django_server()
    except KeyboardInterrupt:
        print("\n[DAMA] Arret manuel detecte. Fermeture du serveur...")
        sys.exit(0)
    except Exception as e:
        print(f"[DAMA] Erreur serveur: {e}")
        sys.exit(1)
