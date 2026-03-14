from django.conf import settings
from datetime import datetime

def site_info(request):
    """Informations du site pour les templates"""
    return {
        'site_name': 'BornSafe Mairie',
        'site_description': 'Système de gestion des actes de naissance',
        'current_year': datetime.now().year,
        'gabon_regions': [
            'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié', 
            'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime',
            'Woleu-Ntem'
        ],
    }
