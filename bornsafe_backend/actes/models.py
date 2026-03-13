from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
import uuid
from provinces.models import Province
from django.conf import settings
import os

def acte_pdf_path(instance, filename):
    """Génère un chemin unique pour le fichier PDF"""
    ext = filename.split('.')[-1]
    filename = f"{instance.numero_acte}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('actes_pdfs', filename)

def qr_code_path(instance, filename):
    """Génère un chemin unique pour le QR code"""
    ext = filename.split('.')[-1]
    filename = f"qr_{instance.numero_acte}.{ext}"
    return os.path.join('qr_codes', filename)

class ActeNaissance(models.Model):
    """Modèle pour les actes de naissance"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    numero_acte = models.CharField(
        max_length=100, 
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(5)],
        help_text="Numéro unique de l'acte de naissance"
    )
    
    nom = models.CharField(max_length=100, db_index=True)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(db_index=True)
    lieu_naissance = models.CharField(max_length=100)
    
    province = models.ForeignKey(
        Province, 
        on_delete=models.PROTECT,  # PROTECT au lieu de CASCADE
        related_name='actes_naissance'
    )
    
    # Fichiers
    fichier_pdf = models.FileField(
        upload_to=acte_pdf_path, 
        null=True, 
        blank=True
    )
    
    qr_code = models.ImageField(
        upload_to=qr_code_path, 
        null=True, 
        blank=True
    )
    
    # Métadonnées
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='created_actes', 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='modified_actes', 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    # Statut
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('annule', 'Annulé'),
    ]
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='brouillon',
        db_index=True
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['numero_acte', 'nom']),
            models.Index(fields=['province', 'date_naissance']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.numero_acte} - {self.nom} {self.prenom}"
    
    def save(self, *args, **kwargs):
        """Surcharge pour mettre à jour updated_at"""
        if not self._state.adding:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_qr_data(self):
        """Génère les données pour le QR code"""
        return f"BornSafe|{self.numero_acte}|{self.nom}|{self.prenom}|{self.date_naissance}"
