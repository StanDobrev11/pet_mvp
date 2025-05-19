from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from datetime import date

from pet_mvp.drugs.models import BloodTest


class BloodTestModelTests(TestCase):
    """
    Tests for the BloodTest model.
    """

    def setUp(self):
        """Set up test data."""
        self.blood_test_data = {
            'result': 'Normal blood count',
            'date_conducted': date(2023, 5, 15),
            'additional_notes': 'No abnormalities detected',
            'white_blood_cells': 10.5,
            'red_blood_cells': 5.2,
            'hemoglobin': 14.5,
            'platelets': 250.0
        }

    def test_blood_test_creation(self):
        """Test creating a blood test with valid data."""
        blood_test = BloodTest.objects.create(**self.blood_test_data)

        self.assertEqual(blood_test.result, self.blood_test_data['result'])
        self.assertEqual(blood_test.date_conducted, self.blood_test_data['date_conducted'])
        self.assertEqual(blood_test.additional_notes, self.blood_test_data['additional_notes'])
        self.assertEqual(float(blood_test.white_blood_cells), self.blood_test_data['white_blood_cells'])
        self.assertEqual(float(blood_test.red_blood_cells), self.blood_test_data['red_blood_cells'])
        self.assertEqual(float(blood_test.hemoglobin), self.blood_test_data['hemoglobin'])
        self.assertEqual(float(blood_test.platelets), self.blood_test_data['platelets'])

    def test_blood_test_str_method(self):
        """Test the __str__ method of the BloodTest model."""
        blood_test = BloodTest.objects.create(**self.blood_test_data)

        expected_str = f"Blood Test conducted on {self.blood_test_data['date_conducted']}"
        self.assertEqual(str(blood_test), expected_str)

    def test_blood_test_inheritance(self):
        """Test that BloodTest inherits from BaseTest."""
        blood_test = BloodTest.objects.create(**self.blood_test_data)

        # Check that the blood test has the attributes from BaseTest
        self.assertTrue(hasattr(blood_test, 'result'))
        self.assertTrue(hasattr(blood_test, 'date_conducted'))
        self.assertTrue(hasattr(blood_test, 'additional_notes'))

    def test_blood_test_name_property(self):
        """Test the name property of the BloodTest model."""
        blood_test = BloodTest.objects.create(**self.blood_test_data)

        self.assertEqual(blood_test.name, "Blood Test")

    def test_blood_test_optional_fields(self):
        """Test that optional fields can be null or blank."""
        # Create a blood test with minimal required fields
        minimal_data = {
            'result': 'Minimal test',
            'date_conducted': date(2023, 5, 15)
        }
        blood_test = BloodTest.objects.create(**minimal_data)

        # Check that optional fields are None
        self.assertIsNone(blood_test.additional_notes)
        self.assertIsNone(blood_test.white_blood_cells)
        self.assertIsNone(blood_test.red_blood_cells)
        self.assertIsNone(blood_test.hemoglobin)
        self.assertIsNone(blood_test.platelets)

        # Check that the test was created successfully
        self.assertEqual(blood_test.result, minimal_data['result'])
        self.assertEqual(blood_test.date_conducted, minimal_data['date_conducted'])