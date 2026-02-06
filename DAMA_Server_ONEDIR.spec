# -*- mode: python ; coding: utf-8 -*-
# Configuration PyInstaller ONEDIR pour démarrage ULTRA-RAPIDE
# Format: Dossier avec exécutable + dépendances (pas d'extraction = démarrage instantané)

import sys
from pathlib import Path

block_cipher = None

# Chemins
django_dir = Path('blog_pos')
static_files = django_dir / 'order' / 'static'
templates_files = django_dir

a = Analysis(
    ['blog_pos/Welto.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Templates Django (seulement ceux qui existent)
        ('blog_pos/order/templates', 'order/templates'),
        ('blog_pos/users/templates', 'users/templates'),
        ('blog_pos/client/templates', 'client/templates'),
        ('blog_pos/aprovision/templates', 'aprovision/templates'),
        
        # Static files Django
        ('blog_pos/order/static', 'order/static'),
        ('blog_pos/staticfiles', 'staticfiles'),
        
        # Templates django_tables2 (requis pour les tableaux)
        # Collecte depuis le site-packages
        ('dama_env/Lib/site-packages/django_tables2/templates', 'django_tables2/templates'),
        
        # Base de données (si SQLite)
        ('blog_pos/db.sqlite3', '.'),
        
        # Settings et configuration Django
        ('blog_pos/blog_pos', 'blog_pos'),
        ('blog_pos/order', 'order'),
        ('blog_pos/users', 'users'), 
        ('blog_pos/client', 'client'),
        ('blog_pos/aprovision', 'aprovision'),
        ('blog_pos/product', 'product'),
    ],
    hiddenimports=[
        'django.core.management',
        'django.contrib.staticfiles.handlers',
        'blog_pos.settings',
        'blog_pos.urls',
        'blog_pos.asgi',
        'order.models',
        'order.views',
        'product.models',
        'product.views',
        'client.models',
        'client.views',
        'users.models',
        'users.views',
        'aprovision.models',
        'aprovision.views',
        'uvicorn',
        'uvicorn.lifespan.on',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.http.h11_impl',
        'click',
        'h11',
        # Ajout des modules manquants
        'whitenoise',
        'whitenoise.middleware',
        'whitenoise.storage',
        'django_tables2',
        'django_tables2.templatetags',
        'django_tables2.templatetags.django_tables2',
        # PDF Generation
        'xhtml2pdf',
        'xhtml2pdf.pisa',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ONEDIR: Exécutable sans binaires (seront dans COLLECT)
exe = EXE(
    pyz,
    a.scripts,
    [],                        # PAS de binaries ici (c'est la clé pour ONEDIR)
    exclude_binaries=True,     # OBLIGATOIRE pour ONEDIR
    name='DAMA_Django_Server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # Pas de console pour desktop
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='desktop_app/assets/logo.ico',
    version_file=None,
)

# COLLECT: Rassemble tout dans un dossier (ONEDIR)
# C'est ce qui rend le démarrage ultra-rapide (pas d'extraction)
coll = COLLECT(
    exe,                    # L'exécutable
    a.binaries,            # Toutes les DLL et bibliothèques
    a.zipfiles,            # Fichiers compressés
    a.datas,              # Données (templates, static, DB)
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DAMA_Django_Server',  # Nom du dossier final
)
