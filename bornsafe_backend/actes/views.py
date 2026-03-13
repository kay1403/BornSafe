from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from .models import ActeNaissance
from .serializers import (
    ActeNaissanceListSerializer, 
    ActeNaissanceDetailSerializer,
    ActeNaissanceCreateUpdateSerializer,
    ActeNaissanceVerifySerializer
)
from accounts.permissions import IsMairieOrSuperAdmin
from .utils import generate_qr_code, generate_pdf
import logging

logger = logging.getLogger('bornsafe')

class ActeNaissanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les actes de naissance
    """
    queryset = ActeNaissance.objects.select_related(
        'province', 'created_by', 'modified_by'
    ).all()
    
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    filterset_fields = ['province', 'status', 'date_naissance']
    search_fields = ['numero_acte', 'nom', 'prenom', 'lieu_naissance']
    ordering_fields = ['created_at', 'date_naissance', 'nom']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ActeNaissanceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ActeNaissanceCreateUpdateSerializer
        elif self.action == 'verify':
            return ActeNaissanceVerifySerializer
        return ActeNaissanceDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'validate']:
            permission_classes = [IsMairieOrSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Optimisation des requêtes"""
        queryset = super().get_queryset()
        
        # Filtrage par rôle
        user = self.request.user
        if user.role == 'mairie':
            # Les mairies voient seulement les actes qu'elles ont créés
            queryset = queryset.filter(created_by=user)
        elif user.role == 'user':
            # Les utilisateurs voient seulement les actes validés
            queryset = queryset.filter(status='valide')
        
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        """Création avec utilisateur"""
        instance = serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user
        )
        
        # Générer le PDF et QR code en arrière-plan
        self._generate_documents(instance)
        
        logger.info(f"Acte créé: {instance.numero_acte} par {self.request.user.username}")

    @transaction.atomic
    def perform_update(self, serializer):
        """Mise à jour avec utilisateur"""
        instance = serializer.save(modified_by=self.request.user)
        
        # Invalider le cache si nécessaire
        cache.delete(f'acte_{instance.id}')
        
        logger.info(f"Acte mis à jour: {instance.numero_acte} par {self.request.user.username}")

    def _generate_documents(self, instance):
        """Génère les documents (PDF et QR code)"""
        try:
            # Générer le QR code
            generate_qr_code(instance)
            
            # Générer le PDF
            generate_pdf(instance)
            
            instance.save(update_fields=['qr_code', 'fichier_pdf'])
        except Exception as e:
            logger.error(f"Erreur génération documents pour {instance.numero_acte}: {str(e)}")

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Vérifier un acte de naissance"""
        serializer = ActeNaissanceVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        acte = serializer.validated_data['acte']
        
        # Mettre en cache pour les prochaines vérifications
        cache.set(f'verified_{acte.numero_acte}', True, timeout=3600)
        
        logger.info(f"Acte vérifié: {acte.numero_acte} par {request.user.username}")
        
        return Response({
            'status': 'conforme',
            'message': 'Acte de naissance authentique',
            'acte': ActeNaissanceDetailSerializer(acte).data
        })

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valider un acte (le passer du statut brouillon à validé)"""
        acte = self.get_object()
        
        if acte.status != 'brouillon':
            return Response(
                {'error': "Cet acte ne peut pas être validé"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        acte.status = 'valide'
        acte.modified_by = request.user
        acte.save()
        
        logger.info(f"Acte validé: {acte.numero_acte} par {request.user.username}")
        
        return Response({
            'message': 'Acte validé avec succès',
            'acte': ActeNaissanceDetailSerializer(acte).data
        })

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Télécharger le PDF d'un acte"""
        acte = self.get_object()
        
        if not acte.fichier_pdf:
            return Response(
                {'error': "PDF non disponible"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"PDF téléchargé: {acte.numero_acte} par {request.user.username}")
        
        from django.http import FileResponse
        return FileResponse(
            acte.fichier_pdf, 
            as_attachment=True,
            filename=f"acte_{acte.numero_acte}.pdf"
        )

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Récupérer le QR code d'un acte"""
        acte = self.get_object()
        
        if not acte.qr_code:
            return Response(
                {'error': "QR code non disponible"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.http import FileResponse
        return FileResponse(acte.qr_code, content_type='image/png')
