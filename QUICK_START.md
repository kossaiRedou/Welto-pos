# ⚡ Quick Start - 5 Étapes pour Déployer WELTO

## ✅ Ce qui est Fait

- ✅ Code modifié pour AppData et mises à jour
- ✅ Dépôt `welto-pos` existe (code source)
- ✅ Dépôt `welto-distribution` créé (vide pour l'instant)
- ✅ package.json configuré: `"repo": "welto-distribution"`
- ✅ GitHub Actions workflow créé

---

## 🎯 À Faire Maintenant (30 minutes)

### 1️⃣ Créer le Token GitHub (2 min)

```
1. https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Name: WELTO Distribution Token
4. Scopes: ✅ repo
5. Generate → COPIER LE TOKEN
```

### 2️⃣ Ajouter le Secret (1 min)

```
1. https://github.com/kossaiRedou/welto-pos/settings/secrets/actions
2. "New repository secret"
3. Name: DISTRIBUTION_TOKEN
4. Secret: [Coller le token]
5. Add secret
```

### 3️⃣ Push le Code (2 min)

```bash
cd C:\Users\lenovo\Desktop\DAMA

# Vérifier le remote
git remote -v

# Si pas de remote:
git remote add origin https://github.com/kossaiRedou/welto-pos.git

# Commit et push
git add .
git commit -m "Update: Système mise à jour automatique"
git push origin main
```

### 4️⃣ Activer GitHub Actions (30 sec)

```
1. https://github.com/kossaiRedou/welto-pos
2. Onglet "Actions"
3. "Enable workflows"
```

### 5️⃣ Créer la Release (1 min)

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 🔍 Surveiller (15-20 min)

### Pendant le build:
```
https://github.com/kossaiRedou/welto-pos/actions
→ Voir le workflow en cours
```

### Après le build:
```
https://github.com/kossaiRedou/welto-distribution/releases
→ v1.0.0 devrait apparaître avec les fichiers .exe
```

---

## ✅ C'est Prêt Quand...

Vous verrez dans `welto-distribution`:
- ✅ Release v1.0.0
- ✅ WELTO-Setup-1.0.0.exe
- ✅ WELTO-Portable.exe
- ✅ latest.yml

---

## 🎉 Partager avec les Clients

**URL de téléchargement:**
```
https://github.com/kossaiRedou/welto-distribution/releases/latest
```

---

## 🆘 Problème?

Voir le guide complet: [`GUIDE_RAPIDE_DEPLOYMENT.md`](GUIDE_RAPIDE_DEPLOYMENT.md)

---

**C'est parti! 🚀**
