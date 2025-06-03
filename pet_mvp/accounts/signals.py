from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from pet_mvp.notifications.tasks import send_user_registration_email


@receiver(user_signed_up)
def send_welcome_email_on_signup(request, user, **kwargs):
    # Only send once, when the user signs up (not on subsequent logins)
    send_user_registration_email(user, user.default_language)
