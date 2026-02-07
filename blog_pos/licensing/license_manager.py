"""
WELTO - Système de Licence Simple
Version 1.0 - Clé universelle avec expiration 6 mois
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64
import platform


class LicenseManager:
    """Gestionnaire de licences WELTO"""
    
    def __init__(self):
        # Utiliser userData pour persister la licence entre les mises à jour
        user_data_path = os.getenv('WELTO_USER_DATA')
        if user_data_path:
            # Mode production: userData (Windows: %APPDATA%\WELTO)
            license_dir = user_data_path
        else:
            # Mode développement: dossier de l'application
            license_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.license_file = os.path.join(license_dir, '.welto_license')
        # Clé de chiffrement basée sur une signature de l'application
        self.app_signature = "WELTO_POS_2025_ALIOU_DIALLO_IA"
        self.cipher_key = self._generate_cipher_key()
        
    def _generate_cipher_key(self):
        """Génère une clé de chiffrement basée sur l'app"""
        key_material = (self.app_signature + platform.machine()).encode()
        key_hash = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(key_hash[:32])
    
    def generate_master_license(self, months=6):
        """
        Génère une licence maître (utiliser côté développeur uniquement)
        """
        expiry_date = datetime.now() + timedelta(days=months * 30)
        license_data = {
            'version': '1.0',
            'type': 'MASTER',
            'issued_date': datetime.now().isoformat(),
            'expiry_date': expiry_date.isoformat(),
            'max_installations': 999,  # Illimité pour la v1
            'features': ['pos', 'inventory', 'clients', 'reports', 'pdf'],
            'signature': self._calculate_signature(expiry_date.isoformat())
        }
        
        # Chiffrer les données
        cipher = Fernet(self.cipher_key)
        encrypted_data = cipher.encrypt(json.dumps(license_data).encode())
        
        # Encoder en base64 pour avoir une clé propre
        license_key = base64.urlsafe_b64encode(encrypted_data).decode()
        
        return license_key, license_data
    
    def _calculate_signature(self, expiry_date):
        """Calcule une signature pour vérifier l'intégrité"""
        signature_data = f"{self.app_signature}{expiry_date}WELTO_SECURITY_2025"
        return hashlib.md5(signature_data.encode()).hexdigest()
    
    def validate_license_key(self, license_key):
        """Valide une clé de licence"""
        try:
            # Décoder et déchiffrer
            encrypted_data = base64.urlsafe_b64decode(license_key.encode())
            cipher = Fernet(self.cipher_key)
            decrypted_data = cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Vérifications
            if license_data.get('version') != '1.0':
                return False, "Version de licence incompatible"
            
            # Vérifier la signature
            expected_signature = self._calculate_signature(license_data['expiry_date'])
            if license_data.get('signature') != expected_signature:
                return False, "Licence corrompue ou invalide"
            
            # Vérifier l'expiration
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() > expiry_date:
                return False, f"Licence expirée le {expiry_date.strftime('%d/%m/%Y')}"
            
            return True, license_data
            
        except Exception as e:
            return False, f"Erreur de validation: {str(e)}"
    
    def save_license(self, license_key):
        """Sauvegarde une licence validée"""
        is_valid, result = self.validate_license_key(license_key)
        if not is_valid:
            return False, result
        
        license_data = result
        try:
            # Ajouter des infos système pour le suivi
            license_data['installation_date'] = datetime.now().isoformat()
            license_data['machine_id'] = platform.node()
            license_data['platform'] = platform.platform()
            
            # Chiffrer et sauvegarder
            cipher = Fernet(self.cipher_key)
            encrypted_license = cipher.encrypt(json.dumps(license_data).encode())
            
            with open(self.license_file, 'wb') as f:
                f.write(encrypted_license)
            
            return True, "Licence activée avec succès"
            
        except Exception as e:
            return False, f"Erreur de sauvegarde: {str(e)}"
    
    def get_current_license(self):
        """Récupère la licence actuelle"""
        if not os.path.exists(self.license_file):
            return None, "Aucune licence trouvée"
        
        try:
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()
            
            cipher = Fernet(self.cipher_key)
            decrypted_data = cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Vérifier si la licence est encore valide
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() > expiry_date:
                return None, f"Licence expirée le {expiry_date.strftime('%d/%m/%Y')}"
            
            return license_data, "Licence valide"
            
        except Exception as e:
            return None, f"Erreur de lecture licence: {str(e)}"
    
    def get_license_status(self):
        """Retourne le statut détaillé de la licence"""
        license_data, message = self.get_current_license()
        
        if not license_data:
            return {
                'is_valid': False,
                'message': message,
                'days_remaining': 0
            }
        
        # Calculer les jours restants
        expiry_date = datetime.fromisoformat(license_data['expiry_date'])
        days_remaining = (expiry_date - datetime.now()).days
        
        return {
            'is_valid': True,
            'message': 'Licence valide',
            'days_remaining': days_remaining,
            'expiry_date': expiry_date.strftime('%d/%m/%Y'),
            'type': license_data.get('type', 'UNKNOWN'),
            'installation_date': license_data.get('installation_date', ''),
            'features': license_data.get('features', [])
        }
    
    def remove_license(self):
        """Supprime la licence (pour debugging)"""
        if os.path.exists(self.license_file):
            os.remove(self.license_file)
            return True
        return False


# Fonction utilitaire pour générer une licence (côté développeur)
def generate_welto_license(months=6):
    """Génère une nouvelle licence WELTO"""
    lm = LicenseManager()
    license_key, license_data = lm.generate_master_license(months)
    
    print(f"🔑 LICENCE WELTO GÉNÉRÉE")
    print(f"📅 Valide jusqu'au: {license_data['expiry_date'][:10]}")
    print(f"⏰ Durée: {months} mois")
    print(f"\n🔐 CLÉ DE LICENCE:")
    print(f"{'='*60}")
    print(license_key)
    print(f"{'='*60}")
    print(f"\n💡 Donnez cette clé à vos clients pour activer WELTO")
    
    return license_key


if __name__ == "__main__":
    # Générer une licence de test
    generate_welto_license(6)
