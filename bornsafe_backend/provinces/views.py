from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from .models import Province
from .serializers import ProvinceSerializer

class ProvinceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les provinces.
    - Lecture accessible à tous les utilisateurs authentifiés.
    - Création, modification et suppression réservées aux admins.
    """
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Exemple pour Swagger : description du list endpoint
    @swagger_auto_schema(
        operation_summary="Lister les provinces",
        operation_description="Récupère la liste de toutes les provinces disponibles",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
