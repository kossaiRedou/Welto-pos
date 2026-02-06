"""
Middleware pour vérifier la licence WELTO à chaque requête
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .license_manager import LicenseManager


class LicenseMiddleware:
    """Middleware pour contrôler l'accès selon la licence"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.license_manager = LicenseManager()
        
        # URLs qui ne nécessitent pas de licence
        self.exempt_urls = [
            '/activate-license/',
            '/license-status/',
            '/admin/login/',
            '/static/',
            '/favicon.ico',
            '/users/login/',
            '/users/logout/',
            # ⚠️ /users/setup/ retiré → nécessite licence active
        ]
    
    def __call__(self, request):
        # Vérifier si l’URL est exemptée
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Éviter la boucle de redirection vers /activate-license/
        try:
            activate_url = reverse('activate_license')
            if request.path == activate_url:
                return self.get_response(request)
        except Exception:
            # Si l’URL n’existe pas encore, on ignore
            pass
        
        # Vérifier la licence
        license_status = self.license_manager.get_license_status()
        
        if not license_status['is_valid']:
            # Rediriger vers la page d’activation
            messages.error(request, license_status['message'])
            return redirect('activate_license')
        
        # Ajouter le statut licence au contexte
        request.license_status = license_status
        
        return self.get_response(request)


# Context processor pour avoir les infos de licence dans tous les templates
def license_context_processor(request):
    """Ajoute les informations de licence aux templates"""
    if hasattr(request, 'license_status'):
        return {
            'license_status': request.license_status
        }
    
    # Fallback si pas de middleware
    license_manager = LicenseManager()
    return {
        'license_status': license_manager.get_license_status()
    }
