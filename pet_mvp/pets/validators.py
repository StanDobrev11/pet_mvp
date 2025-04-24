import re
from django.core.exceptions import ValidationError


def validate_passport_number(value):
    """
    Validate the passport number
    Proper format: 'BG01VP123456'
    - First two characters: country code (uppercase letters)
    - Next two characters: digits
    - Next two characters: uppercase letters
    - Last six characters: digits
    """
    pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{6}$'

    if not re.match(pattern, value):
        raise ValidationError(
            f'{value} is not a valid passport number.'
        )


def validate_transponder_code(value):
    """
    Validate the transponder code
    Proper format: XXX XXX XXXXXXXXX
    'COUNTRY-NUMERIC-CODE' followed by manufacturer's code followed by 9-digits unique identifiers
    """

    country_codes = {
        'AT': '040',
        'BE': '056',
        'BG': '100',
        'HR': '191',
        'CY': '196',
        'CZ': '203',
        'DK': '208',
        'EE': '233',
        'FI': '246',
        'FR': '250',
        'DE': '276',
        'GR': '300',
        'HU': '348',
        'IE': '372',
        'IT': '380',
        'LV': '428',
        'LT': '440',
        'LU': '442',
        'MT': '470',
        'NL': '528',
        'PL': '616',
        'PT': '620',
        'RO': '642',
        'SK': '703',
        'SI': '705',
        'ES': '724',
        'SE': '752',
    }

    pattern = re.compile(r'^\d{3}\d{3}\d{9}$')

    if not pattern.match(value):
        raise ValidationError(f'{value} is not a valid transponder number.')

    country_code = value[:3]

    if country_code not in country_codes.values():
        raise ValidationError('Invalid country code')

    # Additional manufacturer code validation can be added here if needed

    # If all checks pass
    return value
