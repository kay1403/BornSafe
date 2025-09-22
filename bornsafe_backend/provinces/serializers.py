from rest_framework import serializers
from .models import Province

class ProvinceSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source='name')  

    class Meta:
        model = Province
        fields = ['id', 'nom']  
