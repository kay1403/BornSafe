from django.db import models
from django.utils import timezone
import uuid
from provinces.models import Province
from django.conf import settings

class ActeNaissance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_acte = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    fichier_pdf = models.FileField(upload_to='actes_pdfs/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_actes', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='modified_actes', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.numero_acte} - {self.nom} {self.prenom}"
