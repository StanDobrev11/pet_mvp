import random
import string
from django.test import TestCase
from pet_mvp.pets.models import Pet
from pet_mvp.accounts.models import AppUser
from pet_mvp.access_codes.utils import generate_access_code
from pet_mvp.access_codes.models import PetAccessCode

class GenerateAccessCodeTest(TestCase):
    def setUp(self):
        # Create a user for the pets
        self.user = AppUser.objects.create_owner(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone_number='1234567890',
            city='Test City',
            country='Test Country'
        )

        # Create some pets
        self.pets = []
        for i in range(5):
            pet = Pet.objects.create(
                name=f'Pet {i}',
                species='Dog',
                breed='Mixed',
                sex='male',
                date_of_birth='2020-01-01',
                color='Brown',
                features='Friendly',
                current_weight=10.5,
                passport_number=f'PASS{i}12345'
            )
            pet.owners.add(self.user)
            self.pets.append(pet)

    def test_generate_unique_access_codes(self):
        """Test that generated access codes are unique across all pets."""
        # Generate access codes for all pets
        access_codes = []
        for pet in self.pets:
            access_code = generate_access_code(pet)
            access_codes.append(access_code.code)

        # Check that all codes are unique
        self.assertEqual(len(access_codes), len(set(access_codes)), 
                         "Generated access codes are not unique")

    def test_regenerate_access_code_for_same_pet(self):
        """Test that regenerating an access code for the same pet returns the existing code if valid."""
        pet = self.pets[0]

        # Generate an access code for the pet
        first_code = generate_access_code(pet)

        # Generate another access code for the same pet
        second_code = generate_access_code(pet)

        # The second code should be the same as the first one since it's still valid
        self.assertEqual(first_code.code, second_code.code, 
                         "Regenerating access code for the same pet should return the existing code if valid")

    def test_generate_new_code_when_expired(self):
        """Test that a new code is generated when the existing one is expired."""
        import datetime
        from django.utils import timezone

        pet = self.pets[0]

        # Generate an access code for the pet
        access_code = generate_access_code(pet)

        # Make the code expire
        access_code.expires_at = timezone.now() - datetime.timedelta(minutes=1)
        access_code.save()

        # Generate a new access code for the pet
        new_access_code = generate_access_code(pet)

        # The new code should be different from the expired one
        self.assertNotEqual(access_code.code, new_access_code.code, 
                            "A new code should be generated when the existing one is expired")
