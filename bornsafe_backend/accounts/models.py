from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone

class User(AbstractUser):
    """Modèle utilisateur amélioré avec validation"""
    
    # Validateur pour le numéro de téléphone
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[phone_regex],
        help_text="Numéro de téléphone au format international"
    )
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('mairie', 'Mairie'),
        ('user', 'Utilisateur'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        db_index=True  # Index pour améliorer les performances des recherches par rôle
    )
    
    # Champs de suivi
    last_activity = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def record_failed_login(self):
        """Enregistre une tentative de connexion échouée"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Verrouiller le compte après 5 tentatives échouées
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'account_locked_until'])
    
    def reset_failed_login_attempts(self):
        """Réinitialise les tentatives de connexion échouées"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def is_account_locked(self):
        """Vérifie si le compte est verrouillé"""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
