import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from pet_mvp.access_codes.models import PetAccessCode


def generate_access_code(pet):
    try:
        access_code = PetAccessCode.objects.get(pet=pet)
        if access_code.is_valid:
            return access_code
        else:
            access_code.delete()

    except ObjectDoesNotExist:
        pass

    code = str(random.randint(100000, 999999))
    expiration_time = timezone.now() + datetime.timedelta(minutes=240)

    return PetAccessCode.objects.create(
        code=code,
        pet=pet,
        expires_at=expiration_time
    )
