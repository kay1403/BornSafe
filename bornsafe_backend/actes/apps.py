# actes/apps.py
from django.apps import AppConfig

class ActesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actes'

    def ready(self):
        import actes.signals
