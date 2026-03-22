# 📱 CENAD App — Guide complet
**Communauté des Étudiants Natifs d'Andapa à Antsiranana**

---

## 🔧 Changements optimisations Android

| Avant | Après | Gain |
|-------|-------|------|
| pandas + numpy | Python pur | -30 MB APK |
| matplotlib | Graphiques natifs Kivy | -20 MB APK |
| scipy | Supprimé | -15 MB APK |
| Chemins fixes | `app_storage_path()` Android | Compatible stockage |

**APK estimé : ~25 MB** (contre ~90 MB avant)

---

## 🏗 Structure du projet

```
cenad_app/
├── main.py
├── db_manager.py          # SQLite + chemins Android
├── analytics.py           # Stats Python pur (sans pandas)
├── buildozer.spec         # Config APK optimisée
├── Build_CENAD_APK.ipynb  # Notebook Colab
├── .github/
│   └── workflows/
│       └── build_apk.yml  # GitHub Actions
├── screens/
│   ├── accueil.py
│   ├── dashboard.py
│   ├── liste_batiment.py
│   ├── liste_promotion.py
│   ├── historique.py
│   ├── etablissements.py
│   └── admin.py
├── data/                  # Créé automatiquement
└── assets/
    ├── logo.png           # À ajouter
    └── icons/             # À ajouter
```

---

## 🚀 Option 1 : GitHub Actions (recommandée)

### Étapes :
1. Créez un dépôt GitHub : `github.com/votre_compte/cenad_app`
2. Poussez tout le projet :
```bash
git init
git add .
git commit -m "CENAD v1.0"
git remote add origin https://github.com/VOTRE_COMPTE/cenad_app.git
git push -u origin main
```
3. GitHub Actions se déclenche automatiquement
4. Allez dans **Actions > Build CENAD APK > Artifacts**
5. Téléchargez `cenad-debug-apk.zip` contenant votre APK

> ✅ Gratuit, ~20-30 min, APK gardé 30 jours

---

## 🌐 Option 2 : Google Colab (sans compte GitHub)

1. Ouvrez [colab.research.google.com](https://colab.research.google.com)
2. **Fichier > Importer le notebook** → choisir `Build_CENAD_APK.ipynb`
3. Exécutez les cellules une par une
4. À l'étape 3, uploadez votre ZIP du projet
5. Attendez ~25 minutes
6. Téléchargez l'APK généré

> ✅ 100% gratuit, pas besoin d'installer quoi que ce soit

---

## 💻 Option 3 : Compilation locale (Ubuntu/WSL)

```bash
# Installer dépendances
sudo apt update
sudo apt install -y python3-pip build-essential git \
    openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libssl-dev libffi-dev cmake

# Installer Buildozer
pip install buildozer cython==0.29.33

# Compiler
cd cenad_app
buildozer android debug

# APK disponible dans bin/
```

---

## 📲 Installer l'APK sur Android

1. Sur votre téléphone : **Paramètres > Sécurité > Sources inconnues** → Activer
2. Copiez l'APK sur le téléphone (USB ou Google Drive)
3. Ouvrez l'APK depuis le gestionnaire de fichiers
4. Installer

---

## 🔐 Sécurité Admin

| Élément | Valeur |
|---------|--------|
| Mot de passe | `cenad2024` |
| Algorithme | SHA-256 |

Pour changer le mot de passe :
```python
import hashlib
print(hashlib.sha256("nouveau_mdp".encode()).hexdigest())
# Remplacez ADMIN_PASSWORD_HASH dans db_manager.py
```

---

## 📊 Fonctionnalités

| Écran | Fonctionnalités |
|-------|----------------|
| **Accueil** | Menu hamburger, navigation |
| **Dashboard** | Stats temps réel, graphiques Kivy natifs, import CSV/ZIP |
| **Bâtiment** | Membres groupés par bâtiment |
| **Promotion** | Membres groupés par promotion |
| **Historique** | Présidents CENAD depuis 2012 |
| **Établissements** | 9 établissements universitaires |
| **Admin** | CRUD complet, export CSV + ZIP avec photos |

---

*© CENAD 2024 — Fondée en 2012 à Antsiranana, Madagascar*
