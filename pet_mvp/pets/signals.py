from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from pet_mvp.pets.models import Pet
from pet_mvp.pets.utils import delete_pet_photo


@receiver(signal=post_delete, sender=Pet)
def cleanup_pet_references(sender, instance, **kwargs):
    """Signal handler to clean up any references when a pet is deleted"""

    delete_pet_photo(instance)
