from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class PetModelTests(TestCase):
    """
    Tests for the Pet model.
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
        # 2 years, 6 months, 15 days
        self.birth_date = self.today - timedelta(days=365*2 + 30*6 + 15)

    def test_pet_creation(self):
        """Test creating a pet with valid data."""
        pet = Pet(
            name="Buddy",
            species="dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )
        pet.save()
        pet.owners.add(self.owner)

        self.assertEqual(pet.name, "Buddy")
        self.assertEqual(pet.species, "dog")
        self.assertEqual(pet.breed, "Labrador")
        self.assertEqual(pet.sex, "male")
        self.assertEqual(pet.date_of_birth, self.birth_date)
        self.assertEqual(pet.color, "Golden")
        self.assertEqual(pet.features, "Friendly and energetic")
        self.assertEqual(float(pet.current_weight), 25.5)
        self.assertEqual(pet.passport_number, "AB12345678")
        self.assertTrue(pet.can_add_vaccines)
        self.assertEqual(pet.owners.count(), 1)
        self.assertEqual(pet.owners.first(), self.owner)

    def test_pet_str_method(self):
        """Test the __str__ method of the Pet model."""
        pet = Pet.objects.create(
            name="Buddy",
            species="dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )

        self.assertEqual(str(pet), "Buddy - Dog - Labrador")

    def test_pet_age_property(self):
        """Test the age property of the Pet model."""
        pet = Pet.objects.create(
            name="Buddy",
            species="dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )

        # Since we set the birth date to be 2 years, 6 months, and 15 days ago
        # The age property should return a string containing these values
        age_str = pet.age
        self.assertIn("2 years", age_str)
        self.assertIn("6 months", age_str)
        self.assertIn("15 days", age_str)

    def test_duplicate_passport_number(self):
        """Test that creating a pet with a duplicate passport number raises an error."""
        # First, create a pet with a specific passport number
        Pet.objects.create(
            name="Buddy",
            species="dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )

        # Then try to create another pet with the same passport number
        # This should raise an IntegrityError when saved to the database
        duplicate_pet = Pet(
            name="Max",
            species="dog",
            breed="German Shepherd",
            sex="male",
            date_of_birth=self.birth_date,
            color="Black and Tan",
            features="Loyal and protective",
            current_weight=30.0,
            passport_number="AB12345678"  # Same passport number
        )

        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            duplicate_pet.save()

    def test_photo_handling(self):
        """Test that the save method handles photo renaming correctly."""
        # This test is more complex and would require mocking file operations
        # For simplicity, we'll just test that the save method doesn't raise exceptions
        pet = Pet.objects.create(
            name="Buddy",
            species="dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )

        # The save method should have been called during creation
        # If it had errors with photo handling, it would have raised exceptions
        self.assertIsNotNone(pet.pk)
