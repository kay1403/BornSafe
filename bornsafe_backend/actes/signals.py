from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ActeNaissance
from .utils import generate_qr_code, generate_pdf
import logging

logger = logging.getLogger('bornsafe')

@receiver(post_save, sender=ActeNaissance)
def generate_documents(sender, instance, created, **kwargs):
    """Génère les documents après la création d'un acte"""
    if created and not instance.qr_code:
        try:
            # Générer le QR code
            generate_qr_code(instance)
            
            # Générer le PDF
            generate_pdf(instance)
            
            # Sauvegarder sans rappeler le signal
            instance.save(update_fields=['qr_code', 'fichier_pdf'])
            logger.info(f"Documents générés pour l'acte {instance.numero_acte}")
        except Exception as e:
            logger.error(f"Erreur génération documents pour {instance.numero_acte}: {str(e)}")
