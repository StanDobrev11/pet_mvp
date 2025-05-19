from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from datetime import date

from pet_mvp.drugs.models import FecalTest


class FecalTestModelTests(TestCase):
    """
    Tests for the FecalTest model.
    """

    def setUp(self):
        """Set up test data."""
        self.fecal_test_data = {
            'result': 'Normal fecal analysis',
            'date_conducted': date(2023, 5, 15),
            'additional_notes': 'No abnormalities detected',
            'consistency': 'Firm',
            'parasites_detected': True,
            'parasite_type': 'Roundworms',
            'blood_presence': False
        }

    def test_fecal_test_creation(self):
        """Test creating a fecal test with valid data."""
        fecal_test = FecalTest.objects.create(**self.fecal_test_data)

        self.assertEqual(fecal_test.result, self.fecal_test_data['result'])
        self.assertEqual(fecal_test.date_conducted, self.fecal_test_data['date_conducted'])
        self.assertEqual(fecal_test.additional_notes, self.fecal_test_data['additional_notes'])
        self.assertEqual(fecal_test.consistency, self.fecal_test_data['consistency'])
        self.assertEqual(fecal_test.parasites_detected, self.fecal_test_data['parasites_detected'])
        self.assertEqual(fecal_test.parasite_type, self.fecal_test_data['parasite_type'])
        self.assertEqual(fecal_test.blood_presence, self.fecal_test_data['blood_presence'])

    def test_fecal_test_str_method(self):
        """Test the __str__ method of the FecalTest model."""
        fecal_test = FecalTest.objects.create(**self.fecal_test_data)

        expected_str = f"Fecal Test conducted on {self.fecal_test_data['date_conducted']}"
        self.assertEqual(str(fecal_test), expected_str)

    def test_fecal_test_inheritance(self):
        """Test that FecalTest inherits from BaseTest."""
        fecal_test = FecalTest.objects.create(**self.fecal_test_data)

        # Check that the fecal test has the attributes from BaseTest
        self.assertTrue(hasattr(fecal_test, 'result'))
        self.assertTrue(hasattr(fecal_test, 'date_conducted'))
        self.assertTrue(hasattr(fecal_test, 'additional_notes'))

    def test_fecal_test_name_property(self):
        """Test the name property of the FecalTest model."""
        fecal_test = FecalTest.objects.create(**self.fecal_test_data)

        self.assertEqual(fecal_test.name, "Fecal Test")

    def test_fecal_test_optional_fields(self):
        """Test that optional fields can be null or blank."""
        # Create a fecal test with minimal required fields
        minimal_data = {
            'result': 'Minimal test',
            'date_conducted': date(2023, 5, 15)
        }
        fecal_test = FecalTest.objects.create(**minimal_data)

        # Check that optional fields have default values or are None
        self.assertIsNone(fecal_test.additional_notes)
        self.assertIsNone(fecal_test.consistency)
        self.assertFalse(fecal_test.parasites_detected)  # Default is False
        self.assertIsNone(fecal_test.parasite_type)
        self.assertFalse(fecal_test.blood_presence)  # Default is False

        # Check that the test was created successfully
        self.assertEqual(fecal_test.result, minimal_data['result'])
        self.assertEqual(fecal_test.date_conducted, minimal_data['date_conducted'])

    def test_fecal_test_boolean_fields(self):
        """Test the boolean fields of the FecalTest model."""
        # Test with parasites_detected=True and blood_presence=False
        fecal_test = FecalTest.objects.create(**self.fecal_test_data)
        self.assertTrue(fecal_test.parasites_detected)
        self.assertFalse(fecal_test.blood_presence)

        # Test with parasites_detected=False and blood_presence=True
        opposite_data = self.fecal_test_data.copy()
        opposite_data['parasites_detected'] = False
        opposite_data['blood_presence'] = True
        opposite_data['result'] = 'Different result'  # Change to make it a different object
        opposite_test = FecalTest.objects.create(**opposite_data)
        self.assertFalse(opposite_test.parasites_detected)
        self.assertTrue(opposite_test.blood_presence)