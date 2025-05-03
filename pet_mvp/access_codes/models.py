from django.db import models
from django.utils import timezone

from pet_mvp.pets.models import Pet


# Create your models here.
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
