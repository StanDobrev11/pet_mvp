from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from pet_mvp.notifications.tasks import send_user_registration_email

UserModel = get_user_model()


@receiver(signal=post_save, sender=UserModel)
def user_registration_signal(sender, instance, created, **kwargs):
    """Signal handler to send email notification on user registration"""

    if created:
        send_user_registration_email(instance)

    return None
