from django.db.models.signals import post_save
from django.dispatch import receiver

from pet_mvp.notifications.tasks import send_medical_record_email
from pet_mvp.records.models import MedicalExaminationRecord


@receiver(signal=post_save, sender=MedicalExaminationRecord)
def medical_record_email_notification(sender, instance, created, **kwargs):
    """Signal handler to send email notification when a new examination is created"""
    # only send email if created
    if created:
        return send_medical_record_email(instance)

    return None
