"""
Vues pour la gestion des licences WELTO
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .license_manager import LicenseManager
import json


def activate_license_view(request):
    """Vue pour activer une licence"""
    license_manager = LicenseManager()
    
    if request.method == 'POST':
        license_key = request.POST.get('license_key', '').strip()
        
        if not license_key:
            messages.error(request, "Veuillez saisir une clé de licence")
            return render(request, 'licensing/activate.html')
        
        # Valider et sauvegarder la licence
        success, message = license_manager.save_license(license_key)
        
        if success:
            messages.success(request, f" {message}")
            return redirect('dashboard')  # Rediriger vers le dashboard principal
        else:
            messages.error(request, f" {message}")
    
    # Vérifier s'il y a déjà une licence valide
    license_status = license_manager.get_license_status()
    
    context = {
        'current_license': license_status if license_status['is_valid'] else None
    }
    
    return render(request, 'licensing/activate.html', context)


@login_required
def license_status_view(request):
    """Vue pour afficher le statut de la licence"""
    license_manager = LicenseManager()
    license_status = license_manager.get_license_status()
    
    return render(request, 'licensing/status.html', {
        'license_status': license_status
    })


@csrf_exempt
def license_status_api(request):
    """API pour récupérer le statut de licence (pour Electron)"""
    license_manager = LicenseManager()
    license_status = license_manager.get_license_status()
    
    return JsonResponse(license_status)


# Vue pour les développeurs (à supprimer en production)
def debug_license_view(request):
    """Vue de debug pour tester les licences (DEV ONLY)"""
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    license_manager = LicenseManager()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            months = int(request.POST.get('months', 6))
            from .license_manager import generate_welto_license
            license_key = generate_welto_license(months)
            messages.success(request, f"Licence générée: {license_key[:50]}...")
            
        elif action == 'remove':
            if license_manager.remove_license():
                messages.success(request, "Licence supprimée")
            else:
                messages.error(request, "Aucune licence à supprimer")
    
    license_status = license_manager.get_license_status()
    
    return render(request, 'licensing/debug.html', {
        'license_status': license_status
    })
