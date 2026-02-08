"""
Filtres personnalisés pour formater les nombres dans les templates Django.
"""
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter(name='format_number')
def format_number(value, decimals=2):
    """
    Formate un nombre avec X décimales et séparateurs de milliers.
    
    Usage dans les templates:
        {{ value|format_number }}          # 2 décimales par défaut
        {{ value|format_number:3 }}        # 3 décimales
    
    Exemples:
        1234.5 -> "1 234.50"
        1000000 -> "1 000 000.00"
        None -> "0.00"
    
    Args:
        value: Le nombre à formater (peut être int, float, Decimal, str)
        decimals: Nombre de décimales (défaut: 2)
    
    Returns:
        str: Le nombre formaté avec séparateurs d'espaces pour les milliers
    """
    try:
        # Gérer les valeurs None ou vides
        if value is None or value == '':
            return '0.00' if decimals == 2 else f'0.{"0" * decimals}'
        
        # Convertir en Decimal pour une précision maximale
        num = Decimal(str(value))
        
        # Formater avec décimales
        formatted = f"{num:,.{decimals}f}"
        
        # Remplacer la virgule (séparateur de milliers) par un espace
        # pour un format français
        formatted = formatted.replace(',', ' ')
        
        return formatted
        
    except (ValueError, InvalidOperation, TypeError):
        # En cas d'erreur, retourner la valeur originale
        return value


@register.filter(name='format_currency')
def format_currency(value, currency='GMD'):
    """
    Formate un nombre avec 2 décimales et ajoute la devise.
    
    Usage dans les templates:
        {{ value|format_currency }}              # Utilise GMD par défaut
        {{ value|format_currency:"EUR" }}        # Spécifie la devise
    
    Args:
        value: Le nombre à formater
        currency: La devise à afficher (défaut: 'GMD')
    
    Returns:
        str: Le nombre formaté avec la devise
    """
    formatted_number = format_number(value, 2)
    return f"{formatted_number} {currency}"


@register.filter(name='format_percent')
def format_percent(value, decimals=1):
    """
    Formate un pourcentage avec X décimales.
    
    Usage dans les templates:
        {{ value|format_percent }}          # 1 décimale par défaut
        {{ value|format_percent:2 }}        # 2 décimales
    
    Args:
        value: Le pourcentage à formater
        decimals: Nombre de décimales (défaut: 1)
    
    Returns:
        str: Le pourcentage formaté
    """
    try:
        if value is None or value == '':
            return '0.0%' if decimals == 1 else f'0.{"0" * decimals}%'
        
        num = Decimal(str(value))
        formatted = f"{num:.{decimals}f}%"
        
        return formatted
        
    except (ValueError, InvalidOperation, TypeError):
        return value
