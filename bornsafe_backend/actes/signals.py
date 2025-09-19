from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ActeNaissance
import qrcode
from io import BytesIO
from django.core.files import File

@receiver(post_save, sender=ActeNaissance)
def generate_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"BornSafe-{instance.numero_acte}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        instance.qr_code.save(f"{instance.numero_acte}.png", File(buffer), save=True)
