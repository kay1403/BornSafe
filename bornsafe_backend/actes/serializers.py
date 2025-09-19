from rest_framework import serializers
from .models import ActeNaissance
from provinces.serializers import ProvinceSerializer
from provinces.models import Province

class ActeNaissanceSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all(), source='province', write_only=True)

    class Meta:
        model = ActeNaissance
        fields = ['id', 'numero_acte', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
                  'province', 'province_id', 'fichier_pdf', 'qr_code', 'created_at']
