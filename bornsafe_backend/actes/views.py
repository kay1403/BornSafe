from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ActeNaissance
from .serializers import ActeNaissanceSerializer
import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from django.http import FileResponse

# Permission personnalisée
from rest_framework.permissions import BasePermission

class IsMairieOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['mairie', 'super_admin'])

class ActeNaissanceViewSet(viewsets.ModelViewSet):
    queryset = ActeNaissance.objects.all().order_by('-created_at')
    serializer_class = ActeNaissanceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['province__name', 'numero_acte', 'nom', 'prenom']
    ordering_fields = ['created_at', 'date_naissance']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsMairieOrSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='verify')
    def verify_acte(self, request):
        numero = request.data.get('numero_acte')
        nom = request.data.get('nom')
        prenom = request.data.get('prenom')
        date_naissance = request.data.get('date_naissance')
        lieu = request.data.get('lieu_naissance')
        province_id = request.data.get('province_id')

        acte = ActeNaissance.objects.filter(
            numero_acte=numero,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            lieu_naissance=lieu,
            province_id=province_id
        ).first()

        if acte:
            if not acte.qr_code:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(f"BornSafe-{acte.numero_acte}")
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer)
                acte.qr_code.save(f"{acte.numero_acte}.png", File(buffer), save=True)

            serializer = ActeNaissanceSerializer(acte)
            return Response({'status': 'conforme', 'acte': serializer.data})

        return Response({'status': 'non conforme'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        acte = self.get_object()
        if not acte.fichier_pdf:
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 750, f"Acte de Naissance: {acte.numero_acte}")
            c.drawString(100, 730, f"Nom: {acte.nom} {acte.prenom}")
            c.drawString(100, 710, f"Date de naissance: {acte.date_naissance}")
            c.drawString(100, 690, f"Lieu: {acte.lieu_naissance}")
            c.drawString(100, 670, f"Province: {acte.province.name}")
            c.showPage()
            c.save()
            buffer.seek(0)
            acte.fichier_pdf.save(f"{acte.numero_acte}.pdf", File(buffer), save=True)
        return FileResponse(acte.fichier_pdf, as_attachment=True)
