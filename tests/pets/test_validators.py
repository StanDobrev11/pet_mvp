from django.test import TestCase
from django.core.exceptions import ValidationError

from pet_mvp.pets.validators import validate_passport_number, validate_transponder_code


class ValidatorsTests(TestCase):
    """
    Tests for the validators in the pets module.
    """

    def test_validate_passport_number_valid(self):
        """Test validate_passport_number with valid passport numbers."""
        # Valid passport numbers
        valid_numbers = [
            'BG01VP123456',
            'DE02AB987654',
            'FR03CD567890'
        ]

        for number in valid_numbers:
            try:
                validate_passport_number(number)
            except ValidationError:
                self.fail(f"validate_passport_number raised ValidationError unexpectedly for {number}")

    def test_validate_passport_number_invalid(self):
        """Test validate_passport_number with invalid passport numbers."""
        invalid_numbers = [
            'BG1VP123456',    # Missing a digit in second part
            'BG01vp12345',    # Too short
            'BG01VP12345',    # 5 digits at end
            'B01VP123456',    # Missing letter
            '1234567890',     # No letters
            'ABCDEFGHIJKL',   # No digits
            '',               # Empty
            'BG01VP1234567',  # Too long
        ]

        for number in invalid_numbers:
            with self.assertRaises(ValidationError, msg=f"Should fail: {number}"):
                validate_passport_number(number)

    def test_validate_transponder_code_valid(self):
        """Test validate_transponder_code with valid transponder codes."""
        # Valid transponder codes (using country codes from the validator)
        valid_codes = [
            '100123123456789',  # Bulgaria
            '276456789012345',  # Germany
            '250789123456789',  # France
        ]

        for code in valid_codes:
            try:
                validate_transponder_code(code)
            except ValidationError:
                self.fail(f"validate_transponder_code raised ValidationError unexpectedly for {code}")

    def test_validate_transponder_code_invalid_format(self):
        """Test validate_transponder_code with codes that have invalid format."""
        # Invalid format transponder codes
        invalid_format_codes = [
            '10012312345678',   # Too short
            '1001231234567890', # Too long
            'ABC123123456789',  # Contains letters
            '100-123-123456789', # Contains hyphens
            '',                 # Empty string
        ]

        for code in invalid_format_codes:
            with self.assertRaises(ValidationError):
                validate_transponder_code(code)

    def test_validate_transponder_code_invalid_country(self):
        """Test validate_transponder_code with codes that have invalid country codes."""
        # Invalid country code transponder codes
        invalid_country_codes = [
            '999123123456789',  # Non-existent country code
            '000123123456789',  # Non-existent country code
        ]

        for code in invalid_country_codes:
            with self.assertRaises(ValidationError):
                validate_transponder_code(code)
