# 🚀 Processus de Release WELTO POS

Ce document décrit le processus complet de release pour WELTO POS, incluant les phases de test (staging) et de déploiement en production.

## 📋 Table des matières

1. [Architecture du Pipeline](#architecture-du-pipeline)
2. [Convention de Nommage](#convention-de-nommage)
3. [Workflow de Release](#workflow-de-release)
4. [Scénarios Courants](#scénarios-courants)
5. [Dépannage](#dépannage)

---

## 🏗️ Architecture du Pipeline

Le système utilise **deux pipelines distincts** pour séparer les phases de test et de production :

### Pipeline Beta/Staging (`.github/workflows/build-beta.yml`)
- **Trigger** : Tags avec suffixe (`v*-beta`, `v*-rc`, `v*-alpha`)
- **Action** : Build complet + Publication en **prerelease**
- **Distribution** : Releases GitHub sur `welto-distribution`
- **Visibilité** : Accessible manuellement, **NON visible par electron-updater**
- **Clients** : **Aucune notification** - Les clients ne voient pas ces versions

### Pipeline Production (`.github/workflows/build-release.yml`)
- **Trigger** : Tags **SANS suffixe** (`v*` uniquement)
- **Validation** : Vérification automatique que le tag ne contient pas de suffixe
- **Action** : Build complet + Publication en **release stable**
- **Distribution** : Releases GitHub sur `welto-distribution`
- **Visibilité** : Pleinement visible par electron-updater
- **Clients** : **Notification automatique** via auto-update

### Configuration electron-updater

```javascript
// desktop_app/src/main.js
autoUpdater.allowPrerelease = false;  // Ignorer les beta/rc/alpha
autoUpdater.channel = 'latest';       // Canal stable uniquement
```

Cette configuration garantit que les clients ne verront **jamais** les versions de test.

---

## 🏷️ Convention de Nommage

### Tags de Test (Prerelease)

| Format | Exemple | Usage |
|--------|---------|-------|
| `v*-beta` | `v10.0.11-beta` | Version beta principale |
| `v*-beta2` | `v10.0.11-beta2` | Deuxième itération beta |
| `v*-rc1` | `v10.0.11-rc1` | Release Candidate 1 |
| `v*-rc2` | `v10.0.11-rc2` | Release Candidate 2 |
| `v*-alpha` | `v10.0.11-alpha` | Version alpha (très instable) |

✅ **Avantages** :
- Plusieurs itérations possibles (beta1, beta2, rc1, rc2...)
- Historique complet des tests
- Aucun risque de notification aux clients

### Tags de Production (Stable)

| Format | Exemple | Usage |
|--------|---------|-------|
| `v*` | `v10.0.11` | Version stable - **Clients alertés** |

⚠️ **ATTENTION** : Un tag de production déclenche **immédiatement** la notification aux clients.

---

## 🔄 Workflow de Release

### Étape 1 : Développement et Tests Locaux

```bash
# 1. Développer les nouvelles fonctionnalités
git add .
git commit -m "Ajout de [fonctionnalité]"

# 2. Tester en local avec npm start
cd desktop_app
npm start
# Vérifier toutes les fonctionnalités

# 3. Commit final
git add .
git commit -m "v10.0.11 - Description des changements"
git push origin main
```

### Étape 2 : Build et Test Staging (Beta)

```bash
# 1. Créer le tag beta
git tag v10.0.11-beta
git push origin v10.0.11-beta
```

✅ **Actions automatiques** :
1. GitHub Actions démarre le build (`.github/workflows/build-beta.yml`)
2. PyInstaller bundle Django
3. Electron Builder package l'app
4. Publication en **prerelease** sur `welto-distribution`
5. Durée : ~20 minutes

📥 **Téléchargement et test** :
1. Aller sur https://github.com/[VOTRE_USERNAME]/welto-distribution/releases
2. Télécharger `WELTO Setup v10.0.11-beta.exe`
3. Installer sur une machine de test
4. Tester **TOUTES** les fonctionnalités critiques :
   - ✅ Connexion/Authentification
   - ✅ Ventes (ajout produits, quantités, paiements)
   - ✅ Gestion stock
   - ✅ Factures PDF
   - ✅ Licence
   - ✅ Migrations base de données
   - ✅ Interface utilisateur

### Étape 3a : Si Problème Détecté

```bash
# 1. Corriger le bug
git add .
git commit -m "Fix: [description du bug]"
git push origin main

# 2. Créer une nouvelle beta
git tag v10.0.11-beta2
git push origin v10.0.11-beta2

# 3. Retour à l'étape 2 (test)
```

### Étape 3b : Validation OK - Production

```bash
# 1. Créer le tag de production
git tag v10.0.11
git push origin v10.0.11
```

✅ **Actions automatiques** :
1. Validation du tag (pas de suffixe beta/rc/alpha)
2. GitHub Actions démarre le build (`.github/workflows/build-release.yml`)
3. Build complet
4. Publication en **release stable** sur `welto-distribution`
5. **Les clients reçoivent la notification** au prochain démarrage

🎉 **C'est terminé !** Les clients verront la mise à jour disponible automatiquement.

---

## 📖 Scénarios Courants

### Scénario 1 : Nouvelle Fonctionnalité Standard

```bash
# Phase de développement
git commit -m "Ajout saisie quantité directe dans les ventes"
git push origin main

# Phase de test
git tag v10.0.11-beta
git push origin v10.0.11-beta
# → Attendre 20 min, télécharger, installer, tester

# Si OK → Production
git tag v10.0.11
git push origin v10.0.11
# → Les clients sont notifiés
```

**Durée totale** : ~30 minutes (20 min build beta + 10 min tests + build prod)

---

### Scénario 2 : Hotfix Urgent (Bug Critique)

Si vous avez **très confiance** (déjà testé localement) :

```bash
# Développement + Test local approfondi
git commit -m "Hotfix: Correction bug critique paiements"
git push origin main

# Production directe (skip beta)
git tag v10.0.12
git push origin v10.0.12
# → Publication immédiate
```

⚠️ **Risque** : Pas de test en conditions réelles. À utiliser **uniquement** pour les hotfix critiques déjà validés localement.

---

### Scénario 3 : Plusieurs Itérations Beta

```bash
# Beta 1
git tag v10.0.11-beta
git push origin v10.0.11-beta
# → Test révèle un problème

# Correction + Beta 2
git commit -m "Fix: Bug interface"
git tag v10.0.11-beta2
git push origin v10.0.11-beta2
# → Test révèle un autre problème

# Correction + Release Candidate 1
git commit -m "Fix: Bug validation"
git tag v10.0.11-rc1
git push origin v10.0.11-rc1
# → Tous les tests passent

# Production
git tag v10.0.11
git push origin v10.0.11
```

**Avantage** : Historique complet de tous les tests effectués.

---

### Scénario 4 : Annuler une Release Beta

Si vous voulez supprimer une beta qui pose problème :

```bash
# Supprimer localement
git tag -d v10.0.11-beta

# Supprimer sur GitHub
git push origin :refs/tags/v10.0.11-beta
```

⚠️ **Note** : Cela ne supprime pas la release GitHub. Pour cela, aller manuellement sur GitHub > Releases > Delete.

---

## 🔧 Dépannage

### Problème : Le build beta a échoué

1. Aller sur https://github.com/[VOTRE_USERNAME]/Welto-pos/actions
2. Cliquer sur le workflow qui a échoué
3. Examiner les logs pour identifier l'erreur
4. Corriger le problème dans le code
5. Créer un nouveau tag beta

### Problème : La production a été déclenchée par erreur

1. **URGENT** : Supprimer immédiatement la release sur `welto-distribution`
2. Les clients qui ont déjà vu la notification peuvent l'ignorer
3. Corriger le problème
4. Créer une nouvelle version stable corrigée

```bash
# Supprimer le tag de production erroné
git tag -d v10.0.11
git push origin :refs/tags/v10.0.11

# Aller manuellement supprimer la release sur GitHub
# https://github.com/[USERNAME]/welto-distribution/releases
```

### Problème : electron-updater détecte les versions beta

Vérifier la configuration dans `desktop_app/src/main.js` :

```javascript
autoUpdater.allowPrerelease = false;  // DOIT être false
autoUpdater.channel = 'latest';       // DOIT être 'latest'
```

Si modifié, recréer une version stable.

### Problème : Le tag de production ne déclenche rien

Vérifier que le tag **ne contient pas** de suffixe :
- ✅ Correct : `v10.0.11`
- ❌ Incorrect : `v10.0.11-stable` (contient un suffixe)

Le pipeline production rejette automatiquement les tags avec suffixe.

---

## 📊 Checklist de Release Complète

### Avant de créer le tag beta

- [ ] Code testé localement avec `npm start`
- [ ] Toutes les fonctionnalités marchent en développement
- [ ] Version incrémentée dans `package.json` et `main.js`
- [ ] Commit poussé sur `main`

### Pendant les tests beta

- [ ] Build réussi sur GitHub Actions
- [ ] Installation de l'exécutable téléchargé
- [ ] Test connexion/authentification
- [ ] Test fonctionnalités principales (ventes, stock, factures)
- [ ] Test migrations base de données
- [ ] Test licence
- [ ] Aucun crash ou erreur critique

### Avant la production

- [ ] Tous les tests beta passent
- [ ] Aucun bug critique détecté
- [ ] Documentation à jour si nécessaire
- [ ] Prêt à notifier les clients

### Après la production

- [ ] Build production réussi
- [ ] Release visible sur `welto-distribution`
- [ ] Vérifier que `prerelease: false`
- [ ] Test de l'auto-update sur un client existant

---

## 🎯 Résumé du Flux

```
Développement → Commit → Push
    ↓
Tag Beta → Build (20min) → Téléchargement → Tests manuels
    ↓                                              ↓
    ↓                                      Bug trouvé? → Correction → Nouvelle Beta
    ↓                                              ↓
    ↓                                          Tous OK
    ↓                                              ↓
Tag Production → Build (20min) → Release publique → Clients notifiés ✅
```

---

## 📞 Support

Pour toute question sur le processus de release :
- Consulter ce document
- Vérifier les logs GitHub Actions
- Examiner les releases sur `welto-distribution`

---

**© 2025 GABITHEX TEAM - Développé par Aliou Diallo**
