# -*- mode: python ; coding: utf-8 -*-
# Configuration PyInstaller ONEDIR pour démarrage ULTRA-RAPIDE
# Format: Dossier avec exécutable + dépendances (pas d'extraction = démarrage instantané)

import sys
import os
from pathlib import Path

block_cipher = None

# Chemins
django_dir = Path('blog_pos')
static_files = django_dir / 'order' / 'static'
templates_files = django_dir

# Templates django_tables2 (requis pour OrderListView, ProductTable, etc.)
import django_tables2
dt2_path = os.path.dirname(django_tables2.__file__)
dt2_templates = os.path.join(dt2_path, 'templates')

a = Analysis(
    ['blog_pos/Welto.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Templates Django (optionnels - collectés s'ils existent)
        # Note: PyInstaller ignorera automatiquement les chemins manquants avec warn_on_missing_imports=False
        
        # Static files Django - Tous les fichiers statiques collectés
        ('blog_pos/staticfiles', 'staticfiles'),
        
        # Templates django_tables2 (bootstrap.html, etc.) - requis pour /order-list/
        (dt2_templates, 'django_tables2/templates'),
        
        # Settings et configuration Django
        ('blog_pos/blog_pos', 'blog_pos'),
        ('blog_pos/order', 'order'),
        ('blog_pos/users', 'users'), 
        ('blog_pos/client', 'client'),
        ('blog_pos/aprovision', 'aprovision'),
        ('blog_pos/product', 'product'),
        ('blog_pos/licensing', 'licensing'),
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
        'licensing.models',
        'licensing.views',
        'licensing.license_manager',
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
        # PDF Generation - xhtml2pdf
        'xhtml2pdf',
        'xhtml2pdf.pisa',
        'xhtml2pdf.document',
        'xhtml2pdf.context',
        'xhtml2pdf.parser',
        'xhtml2pdf.tables',
        'xhtml2pdf.tags',
        # ReportLab Core
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.lib.styles',
        'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.platypus.paragraph',
        'reportlab.platypus.tables',
        'reportlab.platypus.frames',
        # ReportLab Graphics et Barcode (TOUS les modules)
        'reportlab.graphics',
        'reportlab.graphics.barcode',
        'reportlab.graphics.barcode.common',
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.code39',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.eanbc',
        'reportlab.graphics.barcode.qr',
        'reportlab.graphics.barcode.usps',
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.widgets',
        'reportlab.graphics.barcode.ecc200datamatrix',
        'reportlab.graphics.barcode.fourstate',
        'reportlab.graphics.barcode.lto',
        'reportlab.graphics.barcode.ean13',
        'reportlab.graphics.barcode.ean8',
        'reportlab.graphics.barcode.itf',
        'reportlab.graphics.barcode.msi',
        'reportlab.graphics.barcode.code11',
        'reportlab.graphics.barcode.code25',
        # Cryptography pour le système de licence WELTO
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.ciphers.algorithms',
        'cryptography.hazmat.primitives.ciphers.modes',
        'cryptography.hazmat.primitives.padding',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.backends.openssl.backend',
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
