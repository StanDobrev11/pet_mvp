from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from pet_mvp.accounts.models import Clinic
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import QRShareToken, VetPetAccess

import uuid

UserModel = get_user_model()


class PetShareTokenViewsTest(TestCase):

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

        self.other_owner = UserModel.objects.create_owner(
            email='other@example.com',
            password='testpass123',
            first_name='Second',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.pet = Pet.objects.create(
            name='Shared Pet',
            species='Dog',
            breed='Retriever',
            color='Golden',
            date_of_birth='2020-05-01',
            sex='male',
            current_weight='30',
            passport_number='BG99CO123456',
        )

        self.vet = UserModel.objects.create_clinic(
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

        self.pet.owners.add(self.owner)

        self.client_owner = Client()
        self.client_owner.login(email='owner@example.com', password='testpass123')

        self.client_other = Client()
        self.client_other.login(email='other@example.com', password='testpass123')
        self.client_vet = Client()
        self.client_vet.force_login(self.vet)

    def test_generate_share_token_view(self):
        url = reverse('generate-share-qr', args=[self.pet.pk])
        response = self.client_owner.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'access_codes/pet_qr_share.html')
        self.assertIn('qr_code_base64', response.context)
        self.assertIn('pet', response.context)

        # Ensure a token was created
        self.assertTrue(QRShareToken.objects.filter(pet=self.pet).exists())

    def test_generate_share_token_requires_owner(self):
        response = self.client_vet.get(reverse('generate-share-qr', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("must be an owner" in str(m) for m in messages))

    def test_accept_valid_share_token(self):
        token = QRShareToken.objects.create(pet=self.pet)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_other.get(url)
        self.assertRedirects(response, reverse('pet-details', kwargs={'pk': self.pet.pk}))

        self.pet.refresh_from_db()
        self.assertIn(self.other_owner, self.pet.owners.all())

        token.refresh_from_db()
        self.assertTrue(token.used)

    def test_accept_expired_share_token(self):
        token = QRShareToken.objects.create(pet=self.pet)
        token.created_at = timezone.now() - timedelta(minutes=11)
        token.save()

        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_other.get(url)
        self.assertRedirects(response, reverse('dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("expired or already been used" in str(m) for m in messages))

    def test_accept_already_used_token(self):
        token = QRShareToken.objects.create(pet=self.pet, used=True)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_other.get(url)
        self.assertRedirects(response, reverse('dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("expired or already been used" in str(m) for m in messages))

    def test_accept_invalid_token(self):
        url = reverse('accept-share-token', kwargs={'token': uuid.uuid4()})
        response = self.client_other.get(url)
        self.assertRedirects(response, reverse('dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid or expired token" in str(m) for m in messages))

    def test_accept_token_unauthenticated(self):
        self.client_other.logout()
        token = QRShareToken.objects.create(pet=self.pet)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_other.get(url)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_accept_valid_share_token_as_vet(self):
        token = QRShareToken.objects.create(pet=self.pet)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})

        response = self.client_vet.get(url)

        # Should redirect to pet details
        self.assertRedirects(response, reverse('pet-details', kwargs={'pk': self.pet.pk}))

        # Vet should now have temporary access
        access = VetPetAccess.objects.filter(vet=self.vet, pet=self.pet).first()
        self.assertIsNotNone(access)
        self.assertTrue(timezone.now() < access.expires_at)

        # Token should be marked as used
        token.refresh_from_db()
        self.assertTrue(token.used)

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("access to" in str(m) for m in messages))

    def test_vet_accepts_expired_token(self):
        token = QRShareToken.objects.create(pet=self.pet)
        token.created_at = timezone.now() - timedelta(minutes=11)
        token.save()

        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_vet.get(url)

        self.assertRedirects(response, reverse('clinic-dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("expired or already been used" in str(m) for m in messages))

        # Should not grant access
        self.assertFalse(VetPetAccess.objects.filter(vet=self.vet, pet=self.pet).exists())

    def test_vet_accepts_used_token(self):
        token = QRShareToken.objects.create(pet=self.pet, used=True)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_vet.get(url)

        self.assertRedirects(response, reverse('clinic-dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("expired or already been used" in str(m) for m in messages))

    def test_vet_accepts_invalid_token(self):
        invalid_token = uuid.uuid4()
        url = reverse('accept-share-token', kwargs={'token': str(invalid_token)})
        response = self.client_vet.get(url)

        self.assertRedirects(response, reverse('clinic-dashboard'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid or expired token" in str(m) for m in messages))

    def test_vet_accepts_token_unauthenticated(self):
        self.client_vet.logout()
        token = QRShareToken.objects.create(pet=self.pet)
        url = reverse('accept-share-token', kwargs={'token': str(token.token)})
        response = self.client_vet.get(url)

        self.assertRedirects(response, f'/accounts/login/?next={url}')
