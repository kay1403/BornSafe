from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.utils import timezone
import logging

logger = logging.getLogger('bornsafe')
User = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un utilisateur"""
    
    nom_utilisateur = serializers.CharField(source='username', read_only=True)
    nom = serializers.CharField(source='first_name', read_only=True)
    prenom = serializers.CharField(source='last_name', read_only=True)
    telephone = serializers.CharField(source='phone_number', read_only=True)
    role_utilisateur = serializers.CharField(source='role', read_only=True)
    est_admin = serializers.BooleanField(source='is_staff', read_only=True)
    est_actif = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'nom_utilisateur', 'email', 'nom', 'prenom', 
            'telephone', 'role_utilisateur', 'est_admin', 'est_actif',
            'date_joined', 'last_login'
        ]


class EnregistrementSerializer(serializers.ModelSerializer):
    """Serializer pour l'enregistrement d'un utilisateur"""
    
    nom_utilisateur = serializers.CharField(source='username', min_length=3, max_length=50)
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=8)
    confirmation_mot_de_passe = serializers.CharField(write_only=True, required=True)
    nom = serializers.CharField(source='first_name', required=True)
    prenom = serializers.CharField(source='last_name', required=True)
    telephone = serializers.CharField(source='phone_number', required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'nom_utilisateur', 'email', 'mot_de_passe', 'confirmation_mot_de_passe',
            'nom', 'prenom', 'telephone'
        ]

    def validate(self, data):
        """Validation personnalisée"""
        
        # Vérifier que les mots de passe correspondent
        if data.get('password') != data.get('confirmation_password'):
            raise serializers.ValidationError({
                'confirmation_mot_de_passe': "Les mots de passe ne correspondent pas"
            })
        
        # Vérifier la force du mot de passe
        try:
            validate_password(data.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'mot_de_passe': list(e.messages)})
        
        # Vérifier que l'email n'est pas déjà utilisé
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({
                'email': "Cet email est déjà utilisé"
            })
        
        # Vérifier que le nom d'utilisateur n'est pas déjà utilisé
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError({
                'nom_utilisateur': "Ce nom d'utilisateur est déjà pris"
            })
        
        return data

    def create(self, validated_data):
        """Création de l'utilisateur"""
        
        # Supprimer le champ de confirmation
        validated_data.pop('confirmation_password')
        password = validated_data.pop('password')
        
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            role='user',
            is_staff=False,
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        logger.info(f"Nouvel utilisateur créé: {user.username}")
        return user


class AdminCreationSerializer(serializers.ModelSerializer):
    """Serializer pour créer un admin"""
    
    nom_utilisateur = serializers.CharField(source='username', min_length=3, max_length=50)
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=8)
    confirmation_mot_de_passe = serializers.CharField(write_only=True, required=True)
    nom = serializers.CharField(source='first_name', required=True)
    prenom = serializers.CharField(source='last_name', required=True)
    telephone = serializers.CharField(source='phone_number', required=True)
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='mairie')

    class Meta:
        model = User
        fields = [
            'nom_utilisateur', 'email', 'mot_de_passe', 'confirmation_mot_de_passe',
            'nom', 'prenom', 'telephone', 'role'
        ]

    def validate(self, data):
        """Validation similaire à EnregistrementSerializer"""
        if data.get('password') != data.get('confirmation_password'):
            raise serializers.ValidationError({
                'confirmation_mot_de_passe': "Les mots de passe ne correspondent pas"
            })
        
        try:
            validate_password(data.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'mot_de_passe': list(e.messages)})
        
        return data

    def create(self, validated_data):
        """Création de l'admin"""
        validated_data.pop('confirmation_password')
        password = validated_data.pop('password')
        
        admin = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            role=validated_data.get('role', 'mairie'),
            is_staff=True,
            is_superuser=False,
            is_active=True
        )
        admin.set_password(password)
        admin.save()
        
        logger.info(f"Nouvel administrateur créé: {admin.username}")
        return admin


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    
    nom_utilisateur = serializers.CharField(required=True)
    mot_de_passe = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Validation des identifiants"""
        username = data.get('nom_utilisateur')
        password = data.get('mot_de_passe')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("Ce compte est désactivé")
                
                if user.is_account_locked():
                    raise serializers.ValidationError(
                        "Compte temporairement verrouillé. Réessayez plus tard."
                    )
                
                # Réinitialiser les tentatives échouées
                user.reset_failed_login_attempts()
                
            else:
                # Enregistrer la tentative échouée
                try:
                    user = User.objects.get(username=username)
                    user.record_failed_login()
                except User.DoesNotExist:
                    pass
                
                raise serializers.ValidationError("Nom d'utilisateur ou mot de passe incorrect")
        else:
            raise serializers.ValidationError("Veuillez fournir nom d'utilisateur et mot de passe")

        data['user'] = user
        return data
