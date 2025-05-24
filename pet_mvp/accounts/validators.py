from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def phone_number_validator(value):
    if len(value) != 10:
        raise ValidationError(_('Phone number must be of 10 digits'))

    if any(not isinstance(int(v), int) for v in list(value)):
        raise ValidationError(_('Phone number must be only of digits'))


def validate_bulgarian_phone(value):
    if not re.fullmatch(r'^[0-9]{9}$', value):
        raise ValidationError(
            "Enter a valid Bulgarian mobile number (9 digits).")


def normalize_bulgarian_phone(value):
    # Remove non-digit characters
    digits = re.sub(r'\D', '', value)

    # Normalize to national number (starting with 0)
    if digits.startswith('359') and len(digits) == 12:
        digits = '0' + digits[3:]
    elif digits.startswith('00359') and len(digits) == 13:
        digits = '0' + digits[5:]
    elif digits.startswith('0') and len(digits) == 10:
        pass  # Already national format
    elif len(digits) == 9:
        digits = '0' + digits
    else:
        raise ValidationError(_("Invalid Bulgarian mobile number format."))

    # Now reformat to 00359XXXXXXXXX
    normalized = '00359' + digits[1:]

    # Final check: must be 00359 + 8 digits
    if not re.fullmatch(r'^003598[7-9][0-9]{7}$', normalized):
        raise ValidationError(
            _("Enter a valid Bulgarian mobile number (e.g. 0887123456, +359887123456)."))

    return normalized
