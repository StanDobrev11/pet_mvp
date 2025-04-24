from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from medical.passports.models import Passport
from medical.pets.models import Pet


@receiver(signal=post_save, sender=Pet)
def create_passport(sender, instance, created, **kwargs):
    """ the signal will create a passport for the animal """

    if instance.passport_number and created:
        return Passport.objects.create(passport_number=instance.passport_number, pet=instance)

    if instance.passport_number and not created:
        try:
            Passport.objects.get(passport_number=instance.passport_number)
        except ObjectDoesNotExist:
            return Passport.objects.create(passport_number=instance.passport_number, pet=instance)
