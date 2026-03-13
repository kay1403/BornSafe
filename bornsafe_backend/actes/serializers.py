from rest_framework import serializers
from .models import ActeNaissance
from provinces.serializers import ProvinceSerializer
from provinces.models import Province
from django.utils import timezone

class ActeNaissanceListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des actes (champs réduits)"""
    
    province_nom = serializers.CharField(source='province.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ActeNaissance
        fields = [
            'id', 'numero_acte', 'nom', 'prenom', 
            'date_naissance', 'province_nom', 'status',
            'created_at', 'created_by_username'
        ]


class ActeNaissanceDetailSerializer(serializers.ModelSerializer):
    """Serializer pour les détails d'un acte"""
    
    province = ProvinceSerializer(read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), 
        source='province', 
        write_only=True
    )
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    
    class Meta:
        model = ActeNaissance
        fields = [
            'id', 'numero_acte', 'nom', 'prenom', 'date_naissance',
            'lieu_naissance', 'province', 'province_id', 'fichier_pdf',
            'qr_code', 'status', 'created_at', 'updated_at',
            'created_by_username', 'modified_by_username'
        ]
        read_only_fields = ['fichier_pdf', 'qr_code', 'created_at', 'updated_at']


class ActeNaissanceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/mise à jour"""
    
    class Meta:
        model = ActeNaissance
        fields = [
            'numero_acte', 'nom', 'prenom', 'date_naissance',
            'lieu_naissance', 'province', 'status'
        ]
    
    def validate_numero_acte(self, value):
        """Validation du numéro d'acte"""
        if ActeNaissance.objects.filter(numero_acte=value).exists():
            raise serializers.ValidationError("Ce numéro d'acte existe déjà")
        return value
    
    def validate_date_naissance(self, value):
        """Validation de la date de naissance"""
        if value > timezone.now().date():
            raise serializers.ValidationError("La date de naissance ne peut pas être dans le futur")
        return value


class ActeNaissanceVerifySerializer(serializers.Serializer):
    """Serializer pour la vérification d'un acte"""
    
    numero_acte = serializers.CharField(required=True)
    nom = serializers.CharField(required=True)
    prenom = serializers.CharField(required=True)
    date_naissance = serializers.DateField(required=True)
    lieu_naissance = serializers.CharField(required=True)
    province_id = serializers.IntegerField(required=True)
    
    def validate(self, data):
        """Vérification de l'existence de l'acte"""
        acte = ActeNaissance.objects.filter(
            numero_acte=data['numero_acte'],
            nom__iexact=data['nom'],
            prenom__iexact=data['prenom'],
            date_naissance=data['date_naissance'],
            lieu_naissance__iexact=data['lieu_naissance'],
            province_id=data['province_id']
        ).first()
        
        if not acte:
            raise serializers.ValidationError("Acte non trouvé")
        
        if acte.status != 'valide':
            raise serializers.ValidationError("Cet acte n'est pas validé")
        
        data['acte'] = acte
        return data
