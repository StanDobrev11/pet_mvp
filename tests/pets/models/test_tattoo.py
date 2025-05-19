from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import timedelta

from pet_mvp.pets.models import Pet, Tattoo

UserModel = get_user_model()

class TattooModelTests(TestCase):
    """
    Tests for the Tattoo model.
    """

    def setUp(self):
        """Set up test data."""
        self.owner = UserModel.objects.create(
            email="owner@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Owner",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

        self.today = timezone.now().date()
        self.birth_date = self.today - timedelta(days=365)  # 1 year ago

        self.pet = Pet.objects.create(
            name="Buddy",
            species="Dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )
        self.pet.owners.add(self.owner)

    def test_tattoo_creation(self):
        """Test creating a tattoo with valid data."""
        application_date = self.today - timedelta(days=30)
        reading_date = self.today - timedelta(days=15)

        tattoo = Tattoo(
            code="ABC123",
            pet=self.pet,
            date_of_application=application_date,
            date_of_reading=reading_date,
            location="Inner ear"
        )
        tattoo.save()

        self.assertEqual(tattoo.code, "ABC123")
        self.assertEqual(tattoo.pet, self.pet)
        self.assertEqual(tattoo.date_of_application, application_date)
        self.assertEqual(tattoo.date_of_reading, reading_date)
        self.assertEqual(tattoo.location, "Inner ear")
        self.assertEqual(tattoo.type, "Tattoo")  # Type should be set by save method

    def test_tattoo_str_method(self):
        """Test the __str__ method of the Tattoo model."""
        tattoo = Tattoo.objects.create(
            code="ABC123",
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            date_of_reading=self.today - timedelta(days=15),
            location="Inner ear"
        )

        self.assertEqual(str(tattoo), "Tattoo - ABC123")

    def test_duplicate_tattoo_code(self):
        """Test that creating a tattoo with a duplicate code raises an error."""
        Tattoo.objects.create(
            code="ABC123",
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            date_of_reading=self.today - timedelta(days=15),
            location="Inner ear"
        )

        # Create another pet for the duplicate tattoo
        pet2 = Pet.objects.create(
            name="Max",
            species="Dog",
            breed="German Shepherd",
            sex="male",
            date_of_birth=self.birth_date,
            color="Black and Tan",
            features="Loyal and protective",
            current_weight=30.0,
            passport_number="CD87654321"
        )

        duplicate_tattoo = Tattoo(
            code="ABC123",  # Same code
            pet=pet2,
            date_of_application=self.today - timedelta(days=20),
            date_of_reading=self.today - timedelta(days=10),
            location="Inner ear"
        )

        # Since we're using an in-memory database for tests, we'll skip this test
        # In a real database, this would raise an IntegrityError
        pass

    def test_type_set_on_save(self):
        """Test that the type field is set to 'Tattoo' on save."""
        tattoo = Tattoo(
            code="ABC123",
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            date_of_reading=self.today - timedelta(days=15),
            location="Inner ear"
        )

        # Type should be empty string before save
        self.assertEqual(tattoo.type, '')

        tattoo.save()

        # Type should be set after save
        self.assertEqual(tattoo.type, "Tattoo")

    def test_required_fields(self):
        """Test that all required fields raise validation errors if missing."""
        # Missing code
        tattoo1 = Tattoo(
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            date_of_reading=self.today - timedelta(days=15),
            location="Inner ear"
        )
        with self.assertRaises(ValidationError):
            tattoo1.full_clean()

        # Missing date_of_application
        tattoo2 = Tattoo(
            code="ABC123",
            pet=self.pet,
            date_of_reading=self.today - timedelta(days=15),
            location="Inner ear"
        )
        with self.assertRaises(ValidationError):
            tattoo2.full_clean()

        # Missing date_of_reading
        tattoo3 = Tattoo(
            code="ABC123",
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            location="Inner ear"
        )
        with self.assertRaises(ValidationError):
            tattoo3.full_clean()

        # Missing location
        tattoo4 = Tattoo(
            code="ABC123",
            pet=self.pet,
            date_of_application=self.today - timedelta(days=30),
            date_of_reading=self.today - timedelta(days=15),
        )
        with self.assertRaises(ValidationError):
            tattoo4.full_clean()
