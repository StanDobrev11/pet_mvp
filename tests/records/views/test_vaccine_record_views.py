import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware

from pet_mvp.drugs.models import Vaccine
from pet_mvp.pets.models import Pet
from pet_mvp.records.models import VaccinationRecord
from pet_mvp.records.views import VaccineRecordAddView, VaccineRecordEditView


UserModel = get_user_model()

class VaccineRecordViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.clinic = UserModel.objects.create_clinic(
            email='test-clinic@test.com',
            password='1234',
            name='Test Clinic',
            address='123 Some Address',
            is_owner=False,
            phone_number='0887142536',
            city='Varna',
            country='Bulgaria',
            is_approved=True
        )

        self.pet = Pet.objects.create(
            name='Some Test Dog',
            species='dog',
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
        # Create vaccine
        self.vaccine = Vaccine.objects.create(
            name='Test Vaccine',
            suitable_for='dog',
            notes='Test notes',
            recommended_interval_days=365
        )
        
        # Create rabies vaccine
        self.rabies_vaccine = Vaccine.objects.create(
            name='Rabies',
            suitable_for='dog',
            notes='Rabies vaccine notes',
            recommended_interval_days=365
        )

        # Create a vaccine record
        self.vaccine_record = VaccinationRecord.objects.create(
            pet=self.pet,
            vaccine=self.vaccine,
            date_of_vaccination=make_aware(datetime.datetime(2025, 1, 20)),
            valid_from=make_aware(datetime.datetime(2025, 6, 10)),
            valid_until=make_aware(datetime.datetime(2026, 1, 20)),
            manufacturer='Zoetis',
            manufacture_date=make_aware(datetime.datetime(2023, 6, 10)),
            batch_number='P874C09'
        )


        self.pet.owners.add(self.owner)

    def setup_request(self, request, user):
        """Helper method to setup request with user and messages"""
        request.user = user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_add_view_get(self):
        """Test the get request for adding a vaccine record"""
        url = f"{reverse('vaccine-record-add')}?pet_id={self.pet.id}"
        request = self.factory.get(url)
        request = self.setup_request(request, self.clinic)
        
        response = VaccineRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Vaccination Record")

    def test_add_view_post_valid(self):
        """Test posting valid data to create a vaccine record"""
        url = f"{reverse('vaccine-record-add')}?pet_id={self.pet.id}"
        data = {
            'vaccine': self.vaccine.id,
            'date_of_vaccination': '2025-01-20',
            'valid_until': '2026-01-20',
            'manufacturer': 'Zoetis',
            'manufacture_date': '2023-06-10',
            'batch_number': 'P874C09'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.clinic)
        
        response = VaccineRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertEqual(VaccinationRecord.objects.count(), 2)  # One created in setup + one new

    def test_add_view_post_rabies(self):
        """Test posting rabies vaccine data correctly sets valid_from date"""
        url = f"{reverse('vaccine-record-add')}?pet_id={self.pet.id}"
        vaccination_date = datetime.date(2025, 1, 20)
        data = {
            'vaccine': self.rabies_vaccine.id,
            'date_of_vaccination': vaccination_date.strftime('%Y-%m-%d'),
            'valid_until': '2026-01-20',
            'manufacturer': 'Zoetis',
            'manufacture_date': '2023-06-10',
            'batch_number': 'P874C09'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.clinic)
        
        response = VaccineRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        
        # Check that valid_from is set to 21 days after vaccination date
        vaccine_record = VaccinationRecord.objects.get(vaccine=self.rabies_vaccine)
        expected_valid_from = vaccination_date + timedelta(days=21)
        self.assertEqual(vaccine_record.valid_from, expected_valid_from)

    def test_edit_view_get(self):
        """Test the get request for editing a vaccine record"""
        url = reverse('vaccine-record-edit', kwargs={'pk': self.vaccine_record.pk})
        request = self.factory.get(url)
        request = self.setup_request(request, self.clinic)
        
        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Vaccination Record")
        self.assertContains(response, self.vaccine_record.vaccine.name)

    def test_edit_view_post_valid(self):
        """Test posting valid data to update a vaccine record"""
        url = reverse('vaccine-record-edit', kwargs={'pk': self.vaccine_record.pk})
        new_date = datetime.date(2025, 2, 1)
        data = {
            'vaccine': self.vaccine_record.vaccine.id,
            'date_of_vaccination': new_date.strftime('%Y-%m-%d'),
            'valid_until': '2026-02-01',
            'manufacturer': 'Updated Manufacturer',
            'manufacture_date': '2023-07-01',
            'batch_number': 'NEWBATCH123'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.clinic)
        
        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Verify the record was updated
        updated_record = VaccinationRecord.objects.get(pk=self.vaccine_record.pk)
        self.assertEqual(updated_record.date_of_vaccination, new_date)
        self.assertEqual(updated_record.manufacturer, 'Updated Manufacturer')
        self.assertEqual(updated_record.batch_number, 'NEWBATCH123')

    def test_edit_view_unauthorized(self):
        """Test that non-clinic users cannot edit records"""
        url = reverse('vaccine-record-edit', kwargs={'pk': self.vaccine_record.pk})
        request = self.factory.get(url)
        request = self.setup_request(request, self.owner)
        
        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 403)  # Should return forbidden

    def test_add_view_unauthorized(self):
        """Test that users cannot add records when can_add_vaccines is False"""
        self.pet.can_add_vaccines = False
        self.pet.save()
        
        url = f"{reverse('vaccine-record-add')}?pet_id={self.pet.id}"
        request = self.factory.get(url)
        request = self.setup_request(request, self.owner)
        
        response = VaccineRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 403)  # Should return forbidden
