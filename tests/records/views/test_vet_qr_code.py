from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from pet_mvp.accounts.models import Clinic
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import VetAccessToken

UserModel = get_user_model()


class VetAccessQRCodeTests(TestCase):
    def setUp(self):

        self.vet = Clinic.objects.create(
            email='test-clinic@test.com',
            password='1234',
            clinic_name='Test Clinic',
            is_owner=False,
            is_active=True,
            is_approved=True,
            phone_number='0887142536',
            clinic_address='123 Some Address',
            city='Varna',
            country='Bulgaria',
        )

        self.pet = Pet.objects.create(
            name='Some Test Dog',
            species='Dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )

        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )
        self.client_owner = Client()
        self.client_vet = Client()
        self.client_owner.login(email='owner@example.com', password='testpass123')

        self.client_vet.force_login(self.vet)

    def test_generate_qr_code_view(self):
        url = reverse('generate-vet-qr', args=[self.pet.pk])
        response = self.client_owner.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'access_codes/qr_code_display.html')
        self.assertIn('qr_code_base64', response.context)
        self.assertIn('pet', response.context)

    def test_quick_access_redirect_valid_token(self):
        token_obj = VetAccessToken.objects.create(pet=self.pet)
        url = reverse('vet-quick-access') + f'?token={token_obj.token}'
        response = self.client_vet.get(url)
        self.assertRedirects(response, reverse('exam-add') + f'?source=pet&id={token_obj.pet.pk}')

        token_obj.refresh_from_db()
        self.assertTrue(token_obj.used)

    def test_quick_access_invalid_token(self):
        url = reverse('vet-quick-access') + '?token=invalidtoken'
        response = self.client_vet.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'Invalid token.', status_code=403)

    def test_quick_access_expired_token(self):
        token_obj = VetAccessToken.objects.create(
            pet=self.pet,
        )
        token_obj.created_at = timezone.now() - timedelta(minutes=11)
        token_obj.save()
        url = reverse('vet-quick-access') + f'?token={token_obj.token}'
        response = self.client_vet.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.text, 'Token expired or already used.')

    def test_quick_access_token_used_already(self):
        token_obj = VetAccessToken.objects.create(
            pet=self.pet,
            used=True
        )
        url = reverse('vet-quick-access') + f'?token={token_obj.token}'
        response = self.client_vet.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.text, 'Token expired or already used.')

    def test_quick_access_unauthenticated_user(self):
        token_obj = VetAccessToken.objects.create(pet=self.pet)
        url = reverse('vet-quick-access') + f'?token={token_obj.token}'
        response = self.client_owner.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.text, 'Unauthorized access.')
