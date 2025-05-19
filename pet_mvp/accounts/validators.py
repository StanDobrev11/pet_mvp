from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def phone_number_validator(value):
    if len(value) != 10:
        raise ValidationError(_('Phone number must be of 10 digits'))

    if any(not isinstance(int(v), int) for v in list(value)):
        raise ValidationError(_('Phone number must be only of digits'))


