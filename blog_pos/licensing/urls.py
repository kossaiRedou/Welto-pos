"""
URLs pour le système de licences WELTO
"""

from django.urls import path
from . import views

urlpatterns = [
    path('activate-license/', views.activate_license_view, name='activate_license'),
    path('license-status/', views.license_status_view, name='license_status'),
    path('api/license-status/', views.license_status_api, name='license_status_api'),
    
    # URL de debug (à supprimer en production)
    path('debug-license/', views.debug_license_view, name='debug_license'),
]
