from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class AddExistingPetTests(TestCase):
    def setUp(self):
        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.pet = Pet.objects.create(
            name='Test Pet',
            species='dog',
            breed='beagle',
            sex='male',
            date_of_birth='2020-01-01',
            color='Brown',
            features='Friendly',
            current_weight=25,
            passport_number='BG01VP112233'
        )

        self.pending_owner = UserModel.objects.create_owner(
            email='pending@example.com',
            password='testpass123',
            first_name='Pending',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.pet.owners.add(self.owner)

        self.client_owner = Client()
        self.client_pending = Client()

    @patch('pet_mvp.pets.views.send_owner_pet_addition_request')
    def test_add_existing_pet_success(self, mock_send_request):
        self.client_pending.force_login(self.pending_owner)

        url = reverse('pet-add-existing')
        data = {'passport_number': 'BG01VP112233'}

        response = self.client_pending.post(url, data)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn(self.pending_owner, self.pet.pending_owners.all())
        mock_send_request.assert_called_once()

    def test_add_existing_pet_invalid_passport(self):
        self.client_pending.force_login(self.pending_owner)

        url = reverse('pet-add-existing')
        data = {'passport_number': 'INVALID'}

        response = self.client_pending.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['form'].errors['passport_number'],
                         ['INVALID is not a valid passport number. The format must be BG01VP123456.'])
