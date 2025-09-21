from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers import UtilisateurSerializer, EnregistrementSerializer, AdminCreationSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'register':
            return EnregistrementSerializer
        elif self.action == 'create_admin':
            return AdminCreationSerializer
        return UtilisateurSerializer

    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        elif self.action == 'create_admin':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Enregistrement d'un utilisateur classique"""
        serializer = EnregistrementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UtilisateurSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def create_admin(self, request):
        """Création d'un nouvel admin par un admin existant"""
        serializer = AdminCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        return Response(UtilisateurSerializer(admin).data, status=status.HTTP_201_CREATED)
