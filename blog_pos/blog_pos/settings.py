
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f" Configuration WELTO chargée depuis: {env_path}")
else:
    print(f" Fichier de configuration non trouvé: {env_path}")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Détecter si on est en mode PyInstaller bundlé
if getattr(sys, 'frozen', False):
    # Mode PyInstaller: utiliser le chemin du bundle
    BUNDLE_DIR = sys._MEIPASS
    print(f" [WELTO] Mode PyInstaller détecté: {BUNDLE_DIR}")
else:
    BUNDLE_DIR = None

# Configuration userData pour la persistance des données (Windows: %APPDATA%\WELTO)
USER_DATA_PATH = os.getenv('WELTO_USER_DATA', None)

if USER_DATA_PATH:
    # Mode production: utiliser userData (Windows: %APPDATA%\WELTO)
    print(f" [WELTO] Utilisation du dossier userData: {USER_DATA_PATH}")
    DATA_DIR = Path(USER_DATA_PATH) / 'data'
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DATA_DIR / 'db.sqlite3'
    
    # Media dans userData
    MEDIA_DIR = Path(USER_DATA_PATH) / 'media'
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
else:
    # Mode développement: utiliser BASE_DIR
    print(f" [WELTO] Mode développement: utilisation de BASE_DIR")
    DB_PATH = Path(BASE_DIR) / 'db.sqlite3'
    MEDIA_DIR = Path(BASE_DIR) / 'media'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Clé chargée depuis le fichier de configuration sécurisé
SECRET_KEY = os.getenv('SECRET_KEY', 'welto-fallback-key-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '*.localhost',  # Sous-domaines localhost si nécessaire
    # Ajoutez d'autres domaines si nécessaire en production
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'product',
    'order',
    'client',
    'aprovision',
    'users',
    'licensing',  # Système de licences WELTO

    'django_tables2',
]

# Configuration du modèle utilisateur personnalisé
AUTH_USER_MODEL = 'users.User'

# Configuration de l'authentification
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/users/login/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Servir fichiers statiques en production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Désactivé pour desktop (pas nécessaire)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Nécessaire pour les messages Django
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.SetupMiddleware',  # Middleware pour la configuration initiale
    'licensing.middleware.LicenseMiddleware',  # Contrôle des licences WELTO
]

ROOT_URLCONF = 'blog_pos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'licensing.middleware.license_context_processor',  # Infos licence dans templates
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_pos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# Utilise userData en production pour la persistance lors des mises à jour

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DB_PATH),  # Chemin dynamique selon le mode
        'OPTIONS': {
            'init_command': '''
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=NORMAL;
                PRAGMA cache_size=10000;
                PRAGMA temp_store=MEMORY;
                PRAGMA mmap_size=268435456;
            ''',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'fr-fr')  # Français pour l'interface WELTO

TIME_ZONE = os.getenv('TIME_ZONE', 'Africa/Dakar')  # Timezone Afrique de l'Ouest

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Ajuster STATIC_ROOT selon le mode (développement ou PyInstaller bundlé)
if BUNDLE_DIR:
    # Mode PyInstaller: fichiers statiques dans le bundle
    STATIC_ROOT = os.path.join(BUNDLE_DIR, 'staticfiles')
    print(f" [WELTO] Static files path (bundled): {STATIC_ROOT}")
else:
    # Mode développement: fichiers statiques dans BASE_DIR
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration Whitenoise pour les fichiers statiques en production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuration de sécurité pour production (DEBUG=False)
if not DEBUG:
    # Sécurité HTTPS (optionnel pour desktop local)
    SECURE_SSL_REDIRECT = False  # False pour desktop local
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Sessions et cookies
    SESSION_COOKIE_SECURE = False  # False pour desktop local (pas HTTPS)
    CSRF_COOKIE_SECURE = False     # False pour desktop local
    
    # Headers de sécurité
    X_FRAME_OPTIONS = 'DENY'

# Media files (User uploads)
# Utilise userData en production pour la persistance
MEDIA_URL = '/media/'
MEDIA_ROOT = str(MEDIA_DIR)

CURRENCY = os.getenv('CURRENCY', 'GMD')

# Configuration par défaut pour les clés primaires
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'