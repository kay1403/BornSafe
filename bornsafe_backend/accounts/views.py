from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UtilisateurSerializer, EnregistrementSerializer, 
    AdminCreationSerializer, LoginSerializer
)
import logging

logger = logging.getLogger('bornsafe')
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs.
    """
    queryset = User.objects.all().order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.action == 'register':
            return EnregistrementSerializer
        elif self.action == 'create_admin':
            return AdminCreationSerializer
        elif self.action == 'login':
            return LoginSerializer
        return UtilisateurSerializer

    def get_permissions(self):
        if self.action in ['create', 'register', 'login']:
            return [AllowAny()]
        elif self.action == 'create_admin':
            return [IsAdminUser()]
        elif self.action in ['me', 'update_profile', 'change_password']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Enregistrement d'un nouvel utilisateur"""
        serializer = EnregistrementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Générer les tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UtilisateurSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Connexion utilisateur"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Mettre à jour la dernière activité
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])
        
        # Générer les tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Connexion réussie: {user.username}")
        
        return Response({
            'user': UtilisateurSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    @action(detail=False, methods=['post'])
    def create_admin(self, request):
        """Création d'un admin par un super admin"""
        if request.user.role != 'super_admin':
            return Response(
                {"error": "Seuls les super admins peuvent créer des admins"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AdminCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        
        return Response(
            UtilisateurSerializer(admin).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Récupérer le profil de l'utilisateur connecté"""
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Mettre à jour son propre profil"""
        user = request.user
        serializer = UtilisateurSerializer(
            user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"Profil mis à jour: {user.username}")
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Changer son mot de passe"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not user.check_password(old_password):
            return Response(
                {"old_password": "Ancien mot de passe incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {"confirm_password": "Les mots de passe ne correspondent pas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Mot de passe changé: {user.username}")
        return Response(
            {"message": "Mot de passe modifié avec succès"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activer/désactiver un utilisateur (admin uniquement)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = "activé" if user.is_active else "désactivé"
        logger.info(f"Compte {status_text}: {user.username} par {request.user.username}")
        
        return Response({
            "message": f"Compte {status_text}",
            "is_active": user.is_active
        })
