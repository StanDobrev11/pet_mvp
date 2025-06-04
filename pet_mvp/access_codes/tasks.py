from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

from pet_mvp.access_codes.models import QRShareToken


@shared_task
def qr_code_cleanup_task():
    # task that runs daily and cleans up the used share codes
    while True:
        deleted, _ = QRShareToken.objects.filter(used=False, created_at__lt=now() - timedelta(seconds=600))[:1000].delete()
        if deleted == 0:
            break
