from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.signing import Signer

from pet_mvp.pets.models import Pet

UserModel = get_user_model()

class ApprovePetAdditionTests(TestCase):
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

        self.pending_owner = UserModel.objects.create(
            email='pending@example.com',
            password='testpass123',
            first_name='Pending',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.pet = Pet.objects.create(
            name='Rex',
            species='dog',
            breed='beagle',
            sex='male',
            date_of_birth='2020-01-01',
            color='Brown',
            features='Friendly',
            current_weight=25,
            passport_number='BG01EXIST002'
        )

        self.pet.owners.add(self.owner)
        self.pet.pending_owners.add(self.pending_owner)

        self.signer = Signer()
        self.token = self.signer.sign(f'{self.pet.id}:{self.pending_owner.id}')
        self.client = Client()

    def test_approve_pet_addition_success(self):
        url = reverse('approve-pet-addition', args=[self.token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.pending_owner, self.pet.owners.all())
        self.assertNotIn(self.pending_owner, self.pet.pending_owners.all())
        self.assertTemplateUsed(response, "pet/approve_confirmation.html")
        self.assertContains(response, self.pet.name)
        self.assertContains(response, self.pending_owner.get_full_name())

    def test_approve_pet_addition_invalid_token(self):
        url = reverse('approve-pet-addition', args=['invalid-token'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or expired link.", response.content.decode())
