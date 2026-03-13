import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import logging

logger = logging.getLogger('bornsafe')

def generate_qr_code(instance):
    """Génère un QR code pour un acte"""
    try:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        
        # Données structurées
        qr_data = instance.get_qr_data()
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        instance.qr_code.save(
            f"qr_{instance.numero_acte}.png", 
            File(buffer), 
            save=False
        )
        
        logger.debug(f"QR code généré pour {instance.numero_acte}")
        
    except Exception as e:
        logger.error(f"Erreur génération QR code {instance.numero_acte}: {str(e)}")
        raise

def generate_pdf(instance):
    """Génère un PDF pour un acte"""
    try:
        buffer = BytesIO()
        
        # Créer le document PDF
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Titre
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2*cm, "RÉPUBLIQUE DÉMOCRATIQUE DU CONGO")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 3*cm, "ACTE DE NAISSANCE")
        
        # Ligne de séparation
        c.line(2*cm, height - 3.5*cm, width - 2*cm, height - 3.5*cm)
        
        # Informations
        y = height - 5*cm
        line_height = 0.8*cm
        
        c.setFont("Helvetica", 12)
        
        # Numéro d'acte
        c.drawString(2*cm, y, f"Numéro d'acte : {instance.numero_acte}")
        y -= line_height
        
        # Nom et prénom
        c.drawString(2*cm, y, f"Nom : {instance.nom}")
        y -= line_height
        c.drawString(2*cm, y, f"Prénom : {instance.prenom}")
        y -= line_height
        
        # Date et lieu de naissance
        date_str = instance.date_naissance.strftime("%d/%m/%Y")
        c.drawString(2*cm, y, f"Date de naissance : {date_str}")
        y -= line_height
        c.drawString(2*cm, y, f"Lieu de naissance : {instance.lieu_naissance}")
        y -= line_height
        
        # Province
        c.drawString(2*cm, y, f"Province : {instance.province.name}")
        y -= line_height
        
        # Date d'établissement
        created_str = instance.created_at.strftime("%d/%m/%Y")
        c.drawString(2*cm, y, f"Date d'établissement : {created_str}")
        y -= line_height
        
        # QR Code note
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2*cm, 2*cm, "Ce document est authentifié par QR code")
        
        # Finaliser
        c.showPage()
        c.save()
        
        # Sauvegarder
        buffer.seek(0)
        instance.fichier_pdf.save(
            f"acte_{instance.numero_acte}.pdf", 
            File(buffer), 
            save=False
        )
        
        logger.debug(f"PDF généré pour {instance.numero_acte}")
        
    except Exception as e:
        logger.error(f"Erreur génération PDF {instance.numero_acte}: {str(e)}")
        raise
