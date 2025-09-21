from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour afficher un utilisateur"""
    nom_utilisateur = serializers.CharField(source='username', read_only=True)
    nom = serializers.CharField(source='first_name', read_only=True)
    prenom = serializers.CharField(source='last_name', read_only=True)
    telephone = serializers.CharField(source='phone_number', read_only=True)
    est_admin = serializers.BooleanField(source='is_staff', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'nom_utilisateur', 'email', 'nom', 'prenom', 'telephone', 'est_admin']


class EnregistrementSerializer(serializers.ModelSerializer):
    """Serializer pour l'enregistrement d'un utilisateur"""
    nom_utilisateur = serializers.CharField(source='username')
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=6)
    nom = serializers.CharField(source='first_name')
    prenom = serializers.CharField(source='last_name')
    telephone = serializers.CharField(source='phone_number')

    class Meta:
        model = User
        fields = ['nom_utilisateur', 'email', 'mot_de_passe', 'nom', 'prenom', 'telephone']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        user.set_password(validated_data['mot_de_passe'])
        user.save()
        return user


class AdminCreationSerializer(serializers.ModelSerializer):
    """Serializer pour créer un admin"""
    nom_utilisateur = serializers.CharField(source='username')
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=6)
    nom = serializers.CharField(source='first_name')
    prenom = serializers.CharField(source='last_name')
    telephone = serializers.CharField(source='phone_number')

    class Meta:
        model = User
        fields = ['nom_utilisateur', 'email', 'mot_de_passe', 'nom', 'prenom', 'telephone']

    def create(self, validated_data):
        admin = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            is_staff=True,  # Crée directement un admin
            is_superuser=False
        )
        admin.set_password(validated_data['mot_de_passe'])
        admin.save()
        return admin
