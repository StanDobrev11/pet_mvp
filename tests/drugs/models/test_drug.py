from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from pet_mvp.drugs.models import Drug


class DrugModelTests(TestCase):
    """
    Tests for the Drug model.
    """

    def setUp(self):
        """Set up test data."""
        self.drug_data = {
            'name': 'Amoxicillin',
            'notes': 'Antibiotic for bacterial infections'
        }

    def test_drug_creation(self):
        """Test creating a drug with valid data."""
        drug = Drug.objects.create(**self.drug_data)

        self.assertEqual(drug.name, self.drug_data['name'])
        self.assertEqual(drug.notes, self.drug_data['notes'])

    def test_drug_str_method(self):
        """Test the __str__ method of the Drug model."""
        drug = Drug.objects.create(**self.drug_data)

        self.assertEqual(str(drug), self.drug_data['name'])

    def test_drug_inheritance(self):
        """Test that Drug inherits from BaseMedication."""
        drug = Drug.objects.create(**self.drug_data)

        # Check that the drug has the attributes from BaseMedication
        self.assertTrue(hasattr(drug, 'name'))
        self.assertTrue(hasattr(drug, 'notes'))

    def test_drug_unique_name(self):
        """Test that drug names must be unique."""
        # Create a drug
        Drug.objects.create(**self.drug_data)

        # Try to create another drug with the same name
        duplicate_data = self.drug_data.copy()
        duplicate_data['notes'] = 'Different notes'  # Change notes to make sure it's not the same object

        # This should raise an IntegrityError due to the unique constraint on name
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Drug.objects.create(**duplicate_data)
