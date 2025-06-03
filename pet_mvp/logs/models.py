from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class PetAccessLog(models.Model):

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )
    accessed_by = models.ForeignKey(
        to=UserModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Accessed By')
    )
    access_time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Access Time')
    )

    method = models.CharField(
        max_length=50,
        choices=[
            ('qr', 'QR Code'),
            ('link', _('Shared Link')),
            ('owner', _('Owner')),
            ('clinic', _('Clinic View')),
        ],
        default='owner',
        verbose_name=_('Access Method')
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.pet.name} accessed by {self.accessed_by} via {self.method} at {self.access_time}"
