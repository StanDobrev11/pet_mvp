import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

    
def validate_passport_number(value):
    """
    Normalize and validate the passport number.
    Format: 'BG01VP123456'
    - First 2 characters: uppercase letters (country code)
    - Next 2 characters: digits
    - Next 2 characters: uppercase letters
    - Last 6 characters: digits
    Spaces are removed before validation.
    """
    # Normalize: remove all spaces and convert to uppercase
    normalized = re.sub(r'\s+', '', value).upper()

    # Define the pattern
    pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{6}$'

    # Validate against the pattern
    if not re.fullmatch(pattern, normalized):
        raise ValidationError(
            _('%(value)s is not a valid passport number. The format must be BG01VP123456.'),
            params={'value': value},
        )

    return normalized



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
        raise ValidationError(_('{} is not a valid transponder number.').format(value))

    country_code = value[:3]

    if country_code not in country_codes.values():
        raise ValidationError(_('Invalid country code'))

    # Additional manufacturer code validation can be added here if needed

    # If all checks pass
    return value
