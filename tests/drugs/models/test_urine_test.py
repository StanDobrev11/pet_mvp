from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from datetime import date

from pet_mvp.drugs.models import UrineTest


class UrineTestModelTests(TestCase):
    """
    Tests for the UrineTest model.
    """

    def setUp(self):
        """Set up test data."""
        self.urine_test_data = {
            'result': 'Normal urinalysis',
            'date_conducted': date(2023, 5, 15),
            'additional_notes': 'No abnormalities detected',
            'color': 'Yellow',
            'clarity': 'Clear',
            'ph': 6.5,
            'specific_gravity': 1.025,
            'protein': 'Negative',
            'glucose': 'Negative',
            'red_blood_cells': 'Negative',
            'white_blood_cells': 'Negative'
        }

    def test_urine_test_creation(self):
        """Test creating a urine test with valid data."""
        urine_test = UrineTest.objects.create(**self.urine_test_data)

        self.assertEqual(urine_test.result, self.urine_test_data['result'])
        self.assertEqual(urine_test.date_conducted, self.urine_test_data['date_conducted'])
        self.assertEqual(urine_test.additional_notes, self.urine_test_data['additional_notes'])
        self.assertEqual(urine_test.color, self.urine_test_data['color'])
        self.assertEqual(urine_test.clarity, self.urine_test_data['clarity'])
        self.assertEqual(float(urine_test.ph), self.urine_test_data['ph'])
        self.assertEqual(float(urine_test.specific_gravity), self.urine_test_data['specific_gravity'])
        self.assertEqual(urine_test.protein, self.urine_test_data['protein'])
        self.assertEqual(urine_test.glucose, self.urine_test_data['glucose'])
        self.assertEqual(urine_test.red_blood_cells, self.urine_test_data['red_blood_cells'])
        self.assertEqual(urine_test.white_blood_cells, self.urine_test_data['white_blood_cells'])

    def test_urine_test_str_method(self):
        """Test the __str__ method of the UrineTest model."""
        urine_test = UrineTest.objects.create(**self.urine_test_data)

        expected_str = f"Urine Test conducted on {self.urine_test_data['date_conducted']}"
        self.assertEqual(str(urine_test), expected_str)

    def test_urine_test_inheritance(self):
        """Test that UrineTest inherits from BaseTest."""
        urine_test = UrineTest.objects.create(**self.urine_test_data)

        # Check that the urine test has the attributes from BaseTest
        self.assertTrue(hasattr(urine_test, 'result'))
        self.assertTrue(hasattr(urine_test, 'date_conducted'))
        self.assertTrue(hasattr(urine_test, 'additional_notes'))

    def test_urine_test_name_property(self):
        """Test the name property of the UrineTest model."""
        urine_test = UrineTest.objects.create(**self.urine_test_data)

        self.assertEqual(urine_test.name, "Urine Test")

    def test_urine_test_optional_fields(self):
        """Test that optional fields can be null or blank."""
        # Create a urine test with minimal required fields
        minimal_data = {
            'result': 'Minimal test',
            'date_conducted': date(2023, 5, 15)
        }
        urine_test = UrineTest.objects.create(**minimal_data)

        # Check that optional fields are None
        self.assertIsNone(urine_test.additional_notes)
        self.assertIsNone(urine_test.color)
        self.assertIsNone(urine_test.clarity)
        self.assertIsNone(urine_test.ph)
        self.assertIsNone(urine_test.specific_gravity)
        self.assertIsNone(urine_test.protein)
        self.assertIsNone(urine_test.glucose)
        self.assertIsNone(urine_test.red_blood_cells)
        self.assertIsNone(urine_test.white_blood_cells)

        # Check that the test was created successfully
        self.assertEqual(urine_test.result, minimal_data['result'])
        self.assertEqual(urine_test.date_conducted, minimal_data['date_conducted'])