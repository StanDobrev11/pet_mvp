from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model

from pet_mvp.pets.models import Pet
from pet_mvp.accounts.models import AppUser, Clinic
from pet_mvp.logs.models import PetAccessLog

UserModel = get_user_model()


def add_session_to_request(request):
    """Utility to attach session to request for testing session-based logic."""
    middleware = SessionMiddleware(get_response=lambda r: r)
    middleware.process_request(request)
    request.session.save()


class PetDetailViewTests(TestCase):
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

        self.clinic = Clinic.objects.create(
            email='test-clinic@test.com',
            password='1234',
            clinic_name='Test Clinic',
            is_owner=False,
            phone_number='0887142536',
            clinic_address='123 Some Address',
            city='Varna',
            country='Bulgaria',
            is_active=True,
            is_approved=True,
        )

        self.pet = Pet.objects.create(
            name='Test Pet',
            species='dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )

        self.pet.owners.add(self.owner)
        self.url = reverse("pet-details", kwargs={"pk": self.pet.pk})

    def test_owner_access_creates_access_log_once_per_session(self):
        logged_in = self.client.login(email='owner@example.com', password='testpass123')
        self.assertTrue(logged_in)

        # First request should create a log
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PetAccessLog.objects.count(), 1)
        log = PetAccessLog.objects.first()
        self.assertEqual(log.method, 'owner')
        self.assertEqual(log.accessed_by, self.owner)

        # Second request in same session should NOT create a second log
        response = self.client.get(self.url)
        self.assertEqual(PetAccessLog.objects.count(), 1)

    def test_clinic_access_creates_clinic_log(self):
        self.client.force_login(self.clinic)
        # Access pet details
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PetAccessLog.objects.count(), 1)

        log = PetAccessLog.objects.first()
        self.assertEqual(log.method, 'clinic')
        self.assertEqual(log.accessed_by, self.clinic)

    def test_unauthenticated_user_cannot_access_pet_details(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
