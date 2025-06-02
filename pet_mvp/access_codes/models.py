import uuid
from django.utils import timezone
from django.db import models

from pet_mvp.accounts.models import Clinic
from pet_mvp.pets.models import Pet


# Create your models here.
class VetPetAccess(models.Model):

    vet = models.ForeignKey(
        to=Clinic,
        on_delete=models.CASCADE
    )
    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()
    granted_by = models.CharField(max_length=50, choices=(('code', 'Access Code'), ('qr', 'QR Code')))

    def is_active(self):
        return timezone.now() < self.expires_at

class PetAccessCode(models.Model):
    code = models.CharField(
        max_length=6
    )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE,
        related_name='pet_access_code'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @property
    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return self.code


class QRShareToken(models.Model):

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    used = models.BooleanField(
        default=False
    )

    def is_valid(self):
        return (
                not self.used and
                (timezone.now() - self.created_at).total_seconds() < 600  # 10 mins
        )

    def __str__(self):
        return f'Created at: {self.created_at.strftime("%H%M%S")}, Valid: {self.is_valid()}'
