# WELTO POS - Point de Vente Professionnel

> Solution complète de Point de Vente (POS) pour Windows - Développée par Aliou Diallo, Ingénieur IA

## 📋 Description

WELTO est une application desktop professionnelle de gestion de point de vente intégrant:
- Gestion des commandes et ventes
- Gestion des produits et inventaire
- Gestion des clients
- Approvisionnements et dépenses
- Facturation PDF
- Tableau de bord analytique
- Système de licences intégré
- Mises à jour automatiques

## 🏗️ Architecture

- **Backend**: Django 5.2.4 avec serveur Uvicorn ASGI
- **Frontend**: Electron 28.0.0
- **Base de données**: SQLite3 (mode WAL optimisé)
- **Déploiement**: Application standalone Windows

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.12+
- Node.js 18+
- Windows 10/11

### Installation Développement

```bash
# 1. Cloner le dépôt
git clone https://github.com/kossaiRedou/welto-pos.git
cd welto-pos

# 2. Créer l'environnement Python
python -m venv dama_env
dama_env\Scripts\activate

# 3. Installer les dépendances Python
pip install -r blog_pos/requirements.txt

# 4. Installer les dépendances Electron
cd desktop_app
npm install

# 5. Démarrer l'application
npm start
```

## 📦 Build et Distribution

### Build Complet

```bash
# Build Django + Electron
python build_standalone.py
```

Les exécutables seront dans `desktop_app/dist/`.

### Nettoyage

```bash
# Nettoyer les builds temporaires
python cleanup_project.py
```

## 🔄 Système de Mise à Jour

L'application utilise electron-updater pour les mises à jour automatiques:
- Détection automatique des nouvelles versions
- Téléchargement en arrière-plan
- Installation avec backup automatique
- Persistance des données dans `%APPDATA%\WELTO\`

**Dépôt de distribution:** [welto-distribution](https://github.com/kossaiRedou/welto-distribution) (Public)

## 🔐 Système de Licences

WELTO utilise un système de licences intégré:
- Activation par clé de licence
- Validation automatique au démarrage
- Durée configurable (6 mois par défaut)
- Protection contre l'utilisation non autorisée

### Générer une Licence

```bash
cd blog_pos
python -c "from licensing.license_manager import generate_welto_license; generate_welto_license(6)"
```

## 📁 Structure du Projet

```
DAMA/
├── blog_pos/               # Application Django
│   ├── order/              # Module commandes
│   ├── product/            # Module produits
│   ├── client/             # Module clients
│   ├── users/              # Module utilisateurs
│   ├── licensing/          # Système de licences
│   └── aprovision/         # Approvisionnements
│
├── desktop_app/            # Application Electron
│   ├── src/                # Code source Electron
│   └── assets/             # Ressources (logo, icônes)
│
└── .github/workflows/      # CI/CD automatique
```

## 📚 Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Architecture du projet
- [`ARBORESCENCE.md`](ARBORESCENCE.md) - Arborescence détaillée
- [`STRATEGIE_RELEASE.md`](STRATEGIE_RELEASE.md) - Stratégie de release
- [`GUIDE_GITHUB_ACTIONS.md`](GUIDE_GITHUB_ACTIONS.md) - Guide GitHub
- [`GUIDE_MISE_A_JOUR.md`](GUIDE_MISE_A_JOUR.md) - Système de mise à jour
- [`CHECKLIST_DEPLOYMENT.md`](CHECKLIST_DEPLOYMENT.md) - Checklist déploiement

## 🛠️ Technologies

### Backend
- Django 5.2.4
- Uvicorn (ASGI)
- SQLite3
- WhiteNoise
- ReportLab (PDF)

### Frontend
- Electron 28.0.0
- electron-updater
- electron-store
- electron-log

### Build
- PyInstaller 6.16.0
- electron-builder 24.6.4

## 📊 Fonctionnalités

- ✅ Interface POS moderne et intuitive
- ✅ Gestion complète des produits et catégories
- ✅ Gestion des clients et historique
- ✅ Paiements multiples et échelonnés
- ✅ Facturation PDF professionnelle
- ✅ Tableau de bord analytique
- ✅ Gestion des approvisionnements
- ✅ Suivi des dépenses
- ✅ Système de licences intégré
- ✅ Mises à jour automatiques
- ✅ Persistance des données (AppData)
- ✅ Backups automatiques
- ✅ Multi-utilisateurs avec rôles

## 🔄 Workflow de Release

```bash
# 1. Développer
git checkout -b feature/nouvelle-fonctionnalite
# ... coder ...
git commit -m "Add: nouvelle fonctionnalité"

# 2. Fusionner
git checkout main
git merge feature/nouvelle-fonctionnalite

# 3. Créer release
# Modifier package.json: version++
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1
git push origin main
git push origin v1.0.1

# 4. GitHub Actions s'occupe du reste!
```

## 🌍 Persistance des Données (Windows)

Les données sont stockées dans:
```
%APPDATA%\WELTO\
├── data\
│   └── db.sqlite3          # Base de données
├── backups\                # Backups automatiques
└── media\                  # Fichiers uploadés
```

Avantages:
- ✅ Données préservées lors des mises à jour
- ✅ Données préservées lors de désinstallation
- ✅ Backups automatiques avant chaque mise à jour
- ✅ Migrations Django automatiques

## 📞 Support

- **Email**: aliou@gabithex.fr
- **Documentation**: Voir dossier /docs
- **Issues**: GitHub Issues (dans dépôt privé welto-pos)

## 📜 Licence

© 2025 GABITHEX TEAM - Tous droits réservés  
Développé par Aliou Diallo - Ingénieur en Intelligence Artificielle

---

## 🎯 Pour Commencer

1. Lire [`STRATEGIE_RELEASE.md`](STRATEGIE_RELEASE.md)
2. Suivre [`CHECKLIST_DEPLOYMENT.md`](CHECKLIST_DEPLOYMENT.md)
3. Publier votre première release!

**Bonne chance avec WELTO! 🚀**
