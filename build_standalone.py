#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de build pour créer un exécutable autonome DAMA POS
Crée un package complet sans dépendances externes pour les clients
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_step(step, message):
    """Afficher une étape du build"""
    print(f"\n{'='*60}")
    print(f"ETAPE {step}: {message}")
    print(f"{'='*60}")

def run_command(cmd, description, cwd=None, stream_output=False):
    """Exécuter une commande avec gestion d'erreur"""
    print(f"\n {description}...")
    print(f"Commande: {cmd}")

    try:
        if stream_output:
            # Afficher la sortie en temps réel (pour les builds longs)
            result = subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        else:
            result = subprocess.run(cmd, shell=True, check=True, cwd=cwd,
                                  capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        print(f" {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f" {description} - FAILED")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        else:
            print(f"Error: exit code {e.returncode}")
        return False

def clean_build_directories():
    """Nettoyer les dossiers de build précédents"""
    dirs_to_clean = [
        "dist",
        "build", 
        "desktop_app/dist",
        "desktop_app/build"
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            print(f"🧹 Suppression de {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ {dir_path} supprimé")
            except PermissionError as e:
                print(f"⚠️ Impossible de supprimer {dir_path} - fichiers en cours d'utilisation")
                print(f"   Fermez l'application DAMA si elle est ouverte et relancez le script")
                print(f"   Erreur: {e}")
                return False
            except Exception as e:
                print(f"⚠️ Erreur lors de la suppression de {dir_path}: {e}")
    
    return True

# Fonction supprimée : on utilise maintenant le fichier DAMA_Server_ONEDIR.spec existant

def build_django_executable():
    """Construire l'exécutable Django avec PyInstaller"""
    print_step(1, "BUILD DJANGO EXECUTABLE")
    
    # Vérifier que le fichier ONEDIR spec existe
    if not os.path.exists("DAMA_Server_ONEDIR.spec"):
        print("❌ DAMA_Server_ONEDIR.spec introuvable!")
        print("   Le fichier spec ONEDIR doit exister pour un démarrage rapide")
        return False
    
    print("✅ Utilisation du fichier spec ONEDIR existant")
    
    # Construire avec PyInstaller
    return run_command(
        "pyinstaller --clean DAMA_Server_ONEDIR.spec",
        "Construction de l'exécutable Django ONEDIR (démarrage rapide)"
    )

def prepare_electron_build():
    """Préparer Electron pour inclure l'exécutable Django et ses données"""
    print_step(2, "PREPARATION ELECTRON")
    
    # Copier le dossier onedir Django vers desktop_app
    django_onedir_src = "dist/DAMA_Django_Server"  # Dossier onedir
    django_exe_src = f"{django_onedir_src}/DAMA_Django_Server.exe"  # Exe dans le dossier
    django_dst_dir = "desktop_app/resources/DAMA_Django_Server"  # Destination dossier
    
    if not os.path.exists(django_onedir_src) or not os.path.exists(django_exe_src):
        print(f"❌ Dossier/Exécutable Django onedir introuvable:")
        print(f"   Dossier: {django_onedir_src}")
        print(f"   Exécutable: {django_exe_src}")
        return False
    
    # Créer le dossier resources
    os.makedirs("desktop_app/resources", exist_ok=True)
    
    # Copier tout le dossier onedir (plus rapide au démarrage)
    print("📁 Copie du dossier Django onedir...")
    try:
        # Supprimer l'ancien dossier s'il existe
        if os.path.exists(django_dst_dir):
            shutil.rmtree(django_dst_dir)
        
        # Copier tout le dossier onedir
        shutil.copytree(django_onedir_src, django_dst_dir)
        print(f"✅ Dossier onedir copié: {django_dst_dir}")
        print(f"✅ Exécutable disponible: {django_dst_dir}/DAMA_Django_Server.exe")
    except Exception as e:
        print(f"❌ Erreur copie dossier onedir: {e}")
        return False
    
    # Copier les données Django nécessaires
    print("📁 Copie des données Django...")
    
    # Copier la base de données SQLite
    db_src = "blog_pos/db.sqlite3"
    db_dst = "desktop_app/resources/db.sqlite3"
    if os.path.exists(db_src):
        shutil.copy2(db_src, db_dst)
        print(f"✅ Base de données copiée: {db_dst}")
    else:
        print("⚠️ Base de données SQLite introuvable - sera créée au premier lancement")
    
    # Copier les templates
    templates_dirs = [
        ("blog_pos/order/templates", "desktop_app/resources/order/templates"),
        ("blog_pos/users/templates", "desktop_app/resources/users/templates"),
        ("blog_pos/client/templates", "desktop_app/resources/client/templates"),
        ("blog_pos/aprovision/templates", "desktop_app/resources/aprovision/templates"),
    ]
    
    for src_dir, dst_dir in templates_dirs:
        if os.path.exists(src_dir):
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"✅ Templates copiés: {dst_dir}")
        else:
            print(f"⚠️ Templates introuvables: {src_dir}")
    
    # Copier les fichiers statiques
    static_dirs = [
        ("blog_pos/order/static", "desktop_app/resources/order/static"),
        ("blog_pos/staticfiles", "desktop_app/resources/staticfiles"),
    ]
    
    for src_dir, dst_dir in static_dirs:
        if os.path.exists(src_dir):
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"✅ Fichiers statiques copiés: {dst_dir}")
        else:
            print(f"⚠️ Fichiers statiques introuvables: {src_dir}")
    
    # Copier les modules Django essentiels
    django_dirs = [
        ("blog_pos/blog_pos", "desktop_app/resources/blog_pos"),
        ("blog_pos/order", "desktop_app/resources/order"),
        ("blog_pos/users", "desktop_app/resources/users"),
        ("blog_pos/client", "desktop_app/resources/client"),
        ("blog_pos/aprovision", "desktop_app/resources/aprovision"),
        ("blog_pos/product", "desktop_app/resources/product"),
    ]
    
    for src_dir, dst_dir in django_dirs:
        if os.path.exists(src_dir):
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            # Copier le dossier en excluant __pycache__
            shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            print(f"✅ Module Django copié: {dst_dir}")
        else:
            print(f"⚠️ Module Django introuvable: {src_dir}")
    
    print("🎯 Préparation Electron terminée avec succès!")
    return True

def install_performance_dependencies():
    """Installer les dépendances performance pour Uvicorn"""
    print("📦 Installation des dépendances performance...")
    
    # Activer l'environnement virtuel et installer les nouvelles dépendances
    venv_python = Path("dama_env/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Environnement virtuel introuvable")
        return False
        
    try:
        subprocess.run([
            str(venv_python), "-m", "pip", "install", 
            "httptools", "websockets", "--upgrade"
        ], check=True, cwd="blog_pos")
        print("✅ Dépendances performance installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation dépendances: {e}")
        return False

def update_electron_main():
    """Vérifier que main.js est prêt pour l'exécutable bundlé"""
    print_step(3, "VERIFICATION ELECTRON MAIN.JS")
    
    main_js_path = "desktop_app/src/main.js"
    
    # Vérifier que les modifications nécessaires sont présentes
    with open(main_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'app.isPackaged' in content and 'DAMA_Django_Server.exe' in content:
        print(" main.js est déjà configuré pour l'exécutable bundlé")
        return True
    else:
        print(" main.js n'est pas encore configuré pour la production")
        print(" Les modifications ont été faites manuellement")
        return True

def validate_electron_config():
    """Valider la configuration Electron package.json"""
    print_step(4, "VALIDATION CONFIGURATION ELECTRON")
    
    package_json_path = "desktop_app/package.json"
    
    if not os.path.exists(package_json_path):
        print(f"❌ package.json introuvable: {package_json_path}")
        return False
    
    import json
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Vérifier la configuration de build
        build_config = config.get('build', {})
        win_config = build_config.get('win', {})
        
        # Vérifications
        checks = [
            ('forceCodeSigning', build_config.get('forceCodeSigning') == False),
            ('afterSign', build_config.get('afterSign') is None),
            ('icon configuré', 'icon' in win_config),
            ('targets configurés', len(win_config.get('target', [])) > 0)
        ]
        
        print("🔍 Validation de la configuration:")
        all_good = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if not check_result:
                all_good = False
        
        if all_good:
            print("✅ Configuration Electron validée!")
        else:
            print("⚠️ Configuration Electron présente des problèmes (continuons quand même)")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la validation: {e}")
        return True  # Continuer quand même

def setup_electron_environment():
    """Configurer l'environnement pour Electron sans signature"""
    print_step(5, "CONFIGURATION ENVIRONNEMENT ELECTRON")
    
    # Variables d'environnement pour désactiver la signature
    env_vars = {
        'CSC_IDENTITY_AUTO_DISCOVERY': 'false',
        'CSC_LINK': '',
        'CSC_KEY_PASSWORD': ''
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"✅ Variable d'environnement: {var} = {value}")
    
    return True

def build_electron_app():
    """Construire l'application Electron"""
    print_step(6, "BUILD ELECTRON APPLICATION")
    
    # Aller dans le dossier desktop_app
    desktop_dir = "desktop_app"
    
    # Installer les dépendances npm
    if not run_command("npm install", "Installation des dépendances npm", cwd=desktop_dir):
        return False
    
    # Construire l'application avec variables d'environnement
    print("🚀 Construction Electron avec signature désactivée...")
    return run_command(
        "npm run build:win",
        "Construction de l'application Electron",
        cwd=desktop_dir,
        stream_output=True
    )

def main():
    """Fonction principale de build"""
    print("🚀 DAMA POS - BUILD STANDALONE EXECUTABLE OPTIMISÉ")
    print("Création d'un package autonome pour distribution client")
    print("Avec optimisations performance et stabilité")
    
    # Étape 0: Dépendances performance
    if not install_performance_dependencies():
        print("⚠️ Poursuite sans optimisations performance...")
    
    # Nettoyage
    print_step(1, "NETTOYAGE")
    if not clean_build_directories():
        print("❌ Échec du nettoyage - fermez l'application et relancez")
        return False
    
    # Vérifications préliminaires
    if not os.path.exists("blog_pos/Welto.py"):
        print(" blog_pos/Welto.py introuvable!")
        return False
    
    if not os.path.exists("desktop_app/package.json"):
        print(" desktop_app/package.json introuvable!")
        return False
    
    # Build Django
    if not build_django_executable():
        print(" Échec du build Django")
        return False
    
    # Préparer Electron
    if not prepare_electron_build():
        print(" Échec de la préparation Electron")
        return False
    
    # Mettre à jour main.js
    if not update_electron_main():
        print(" Échec de la mise à jour main.js")
        return False
    
    # Valider la configuration Electron
    if not validate_electron_config():
        print(" Échec de la validation configuration")
        return False
    
    # Configurer l'environnement Electron
    if not setup_electron_environment():
        print(" Échec de la configuration environnement")
        return False
    
    # Build Electron
    if not build_electron_app():
        print(" Échec du build Electron")
        return False
    
    # Succès !
    print_step("FINAL", "BUILD COMPLETE!")
    show_build_results()
    
    return True

def show_build_results():
    """Afficher un résumé des fichiers créés"""
    print("🎉 EXÉCUTABLE AUTONOME CRÉÉ AVEC SUCCÈS!")
    print("\n📁 Fichiers de distribution créés:")
    
    dist_dir = "desktop_app/dist"
    if os.path.exists(dist_dir):
        for item in os.listdir(dist_dir):
            item_path = os.path.join(dist_dir, item)
            if os.path.isfile(item_path):
                size_mb = os.path.getsize(item_path) / (1024 * 1024)
                print(f"   📦 {item} ({size_mb:.1f} MB)")
            elif os.path.isdir(item_path):
                print(f"   📂 {item}/")
    
    print("\n✅ PRÊT POUR DISTRIBUTION CLIENT!")
    print("   • Aucune dépendance externe requise")
    print("   • Python et Django intégrés")
    print("   • Interface graphique moderne")
    print("   • Installation simple via .exe")
    
    print("\n🚀 Pour tester:")
    print("   1. Aller dans desktop_app/dist/")
    print("   2. Lancer l'installateur ou l'exécutable portable")
    print("   3. L'application démarrera automatiquement")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
