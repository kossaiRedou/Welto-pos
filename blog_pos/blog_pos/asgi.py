# -*- coding: utf-8 -*-
"""
Configuration ASGI ultra-optimisée pour DAMA Desktop
"""

import os
import django
from django.core.asgi import get_asgi_application
from django.core.cache import cache
from django.db import connection

# Configuration de l'environnement
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_pos.settings')

print("[DAMA] Préchargement Django ASGI - Optimisation démarrage...")

# Préchargement Django avec optimisations
django.setup()

# Pré-initialisation des composants pour démarrage ultra-rapide
try:
    from django.db import connections, transaction
    
    # Pré-chargement de la connection DB avec optimisations
    db_conn = connections['default']
    db_conn.ensure_connection()
    
    # Exécuter les optimisations SQLite WAL
    with db_conn.cursor() as cursor:
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;") 
        cursor.execute("PRAGMA cache_size=10000;")
        cursor.execute("PRAGMA temp_store=MEMORY;")
        cursor.execute("PRAGMA mmap_size=268435456;")
        cursor.execute("SELECT 1;")  # Test simple
    print("[DAMA] Base de données pré-connectée avec optimisations WAL")
    
    # Pré-charger les tables les plus utilisées
    try:
        from order.models import Order
        from product.models import Product
        from users.models import User
        
        # Pré-charger quelques requêtes communes (cache du query planner)
        User.objects.first()
        Product.objects.first() 
        Order.objects.first()
        print("[DAMA] Tables principales pré-chargées")
    except Exception:
        print("[DAMA] Pré-chargement tables: pas de données (normal au premier lancement)")
    
    # Test du cache sans async
    try:
        cache.set('dama_startup_test', 'ready', 1)
        print("[DAMA] Cache initialisé")
    except Exception:
        print("[DAMA] Cache non configuré (normal)")
    
except Exception as e:
    print(f"[DAMA] Warning: Pré-initialisation partielle: {e}")

print("[DAMA] Django ASGI ultra-optimisé - PRÊT pour connexions instantanées")

# Application ASGI optimisée
application = get_asgi_application()
