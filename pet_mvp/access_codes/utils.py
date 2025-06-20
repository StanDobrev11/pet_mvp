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

    # Generate a unique code that doesn't match any other pet's code
    while True:
        code = str(random.randint(100000, 999999))
        # Check if the code is already in use by another pet
        if not PetAccessCode.objects.filter(code=code).exclude(pet=pet).exists():
            break

    # expiration_time = timezone.now() + datetime.timedelta(minutes=240)

    # for testing, removing expiration of the code
    expiration_time = timezone.now() + datetime.timedelta(days=240)

    return PetAccessCode.objects.create(
        code=code,
        pet=pet,
        expires_at=expiration_time
    )
