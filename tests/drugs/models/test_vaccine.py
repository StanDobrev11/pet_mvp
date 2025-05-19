from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from pet_mvp.drugs.models import Vaccine


class VaccineModelTests(TestCase):
    """
    Tests for the Vaccine model.
    """

    def setUp(self):
        """Set up test data."""
        self.vaccine_data = {
            'name': 'Rabies Vaccine',
            'notes': 'Protects against rabies virus',
            'core': True
        }

    def test_vaccine_creation(self):
        """Test creating a vaccine with valid data."""
        vaccine = Vaccine.objects.create(**self.vaccine_data)

        self.assertEqual(vaccine.name, self.vaccine_data['name'])
        self.assertEqual(vaccine.notes, self.vaccine_data['notes'])
        self.assertEqual(vaccine.core, self.vaccine_data['core'])

    def test_vaccine_str_method(self):
        """Test the __str__ method of the Vaccine model."""
        vaccine = Vaccine.objects.create(**self.vaccine_data)

        self.assertEqual(str(vaccine), self.vaccine_data['name'])

    def test_vaccine_inheritance(self):
        """Test that Vaccine inherits from BaseMedication."""
        vaccine = Vaccine.objects.create(**self.vaccine_data)

        # Check that the vaccine has the attributes from BaseMedication
        self.assertTrue(hasattr(vaccine, 'name'))
        self.assertTrue(hasattr(vaccine, 'notes'))

    def test_vaccine_core_field(self):
        """Test the core field of the Vaccine model."""
        # Test with core=True
        vaccine_core = Vaccine.objects.create(**self.vaccine_data)
        self.assertTrue(vaccine_core.core)

        # Test with core=False
        non_core_data = self.vaccine_data.copy()
        non_core_data['core'] = False
        non_core_data['name'] = 'Bordetella Vaccine'  # Change name to avoid unique constraint
        vaccine_non_core = Vaccine.objects.create(**non_core_data)
        self.assertFalse(vaccine_non_core.core)

    def test_vaccine_unique_name(self):
        """Test that vaccine names must be unique."""
        # Create a vaccine
        Vaccine.objects.create(**self.vaccine_data)

        # Try to create another vaccine with the same name
        duplicate_data = self.vaccine_data.copy()
        duplicate_data['notes'] = 'Different notes'  # Change notes to make sure it's not the same object

        # This should raise an IntegrityError due to the unique constraint on name
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Vaccine.objects.create(**duplicate_data)
