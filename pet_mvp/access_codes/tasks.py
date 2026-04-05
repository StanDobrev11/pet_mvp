from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

from pet_mvp.access_codes.models import QRShareToken


@shared_task
def qr_code_cleanup_task():
    # task that runs daily and cleans up expired unused share codes
    cutoff = now() - timedelta(seconds=600)

    while True:
        token_ids = list(
            QRShareToken.objects
            .filter(used=False, created_at__lt=cutoff)
            .order_by("created_at")
            .values_list("id", flat=True)[:1000]
        )

        if not token_ids:
            break

        QRShareToken.objects.filter(id__in=token_ids).delete()
