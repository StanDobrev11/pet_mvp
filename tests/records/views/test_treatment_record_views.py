import datetime
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware

from pet_mvp.drugs.models import Drug
from pet_mvp.pets.models import Pet
from pet_mvp.records.models import MedicationRecord
from pet_mvp.records.views import TreatmentRecordAddView, TreatmentRecordEditView

UserModel = get_user_model()

class TreatmentRecordViewsTest(TestCase):
    def setUp(self):
        """Set up test data."""
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

        # Create regular medication
        self.medication = Drug.objects.create(
            name='Test Medication',
            suitable_for='dog',
            notes='Test notes',
            is_antiparasite=False
        )

        # Create antiparasitic medication
        self.antiparasitic = Drug.objects.create(
            name='Test Antiparasitic',
            suitable_for='dog',
            notes='Test antiparasitic notes',
            is_antiparasite=True
        )

        # Create a treatment record
        self.treatment_record = MedicationRecord.objects.create(
            pet=self.pet,
            medication=self.medication,
            date=make_aware(datetime.datetime(2025, 1, 20)),
            time=datetime.time(10, 30),
            valid_until=make_aware(datetime.datetime(2026, 1, 20)),
            manufacturer='TestMed',
            dosage='10mg'
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
        """Test the get request for adding a treatment record"""
        url = f"{reverse('treatment-record-add')}?pet_id={self.pet.id}"
        request = self.factory.get(url)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Medication / Treatment Record")

    def test_add_view_post_valid(self):
        """Test posting valid data to create a treatment record"""
        url = f"{reverse('treatment-record-add')}?pet_id={self.pet.id}"
        data = {
            'medication': self.medication.id,
            'date': '2025-01-20',
            'time': '10:30',
            'valid_until': '2026-01-20',
            'manufacturer': 'TestMed',
            'dosage': '10mg'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertEqual(MedicationRecord.objects.count(), 2)  # One created in setup + one new

    def test_add_view_post_antiparasitic(self):
        """Test posting antiparasitic medication data with optional fields"""
        url = f"{reverse('treatment-record-add')}?pet_id={self.pet.id}"
        data = {
            'medication': self.antiparasitic.id,
            'date': '2025-01-20',
            'valid_until': '2026-01-20',
            'manufacturer': 'TestMed',
            # Note: time and dosage are optional for antiparasitic medications
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordAddView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect on success

        # Check that record was created without optional fields
        treatment_record = MedicationRecord.objects.get(medication=self.antiparasitic)
        self.assertIsNone(treatment_record.time)
        self.assertFalse(treatment_record.dosage)

    def test_edit_view_get(self):
        """Test the get request for editing a treatment record"""
        url = reverse('treatment-record-edit', kwargs={'pk': self.treatment_record.pk})
        request = self.factory.get(url)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordEditView.as_view()(request, pk=self.treatment_record.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Treatment Record")
        self.assertContains(response, self.treatment_record.medication.name)

    def test_edit_view_post_valid(self):
        """Test posting valid data to update a treatment record"""
        url = reverse('treatment-record-edit', kwargs={'pk': self.treatment_record.pk})
        new_date = datetime.date(2025, 2, 1)
        data = {
            'medication': self.treatment_record.medication.id,
            'date': new_date.strftime('%Y-%m-%d'),
            'time': '11:30',
            'valid_until': '2026-02-01',
            'manufacturer': 'Updated Manufacturer',
            'dosage': '20mg'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordEditView.as_view()(request, pk=self.treatment_record.pk)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Verify the record was updated
        updated_record = MedicationRecord.objects.get(pk=self.treatment_record.pk)
        self.assertEqual(updated_record.date, new_date)
        self.assertEqual(updated_record.time.strftime('%H:%M'), '11:30')
        self.assertEqual(updated_record.manufacturer, 'Updated Manufacturer')
        self.assertEqual(updated_record.dosage, '20mg')

    def test_edit_antiparasitic_keep_optional_fields_empty(self):
        """Test that editing an antiparasitic record can keep optional fields empty"""
        # Create an antiparasitic record first
        antiparasitic_record = MedicationRecord.objects.create(
            pet=self.pet,
            medication=self.antiparasitic,
            date=make_aware(datetime.datetime(2025, 1, 20)),
            valid_until=make_aware(datetime.datetime(2026, 1, 20)),
            manufacturer='TestMed'
        )

        url = reverse('treatment-record-edit', kwargs={'pk': antiparasitic_record.pk})
        data = {
            'medication': self.antiparasitic.id,
            'date': '2025-02-01',
            'valid_until': '2026-02-01',
            'manufacturer': 'Updated Manufacturer',
            # Omitting time and dosage
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordEditView.as_view()(request, pk=antiparasitic_record.pk)
        self.assertEqual(response.status_code, 302)

        # Verify the record was updated and optional fields remain empty
        updated_record = MedicationRecord.objects.get(pk=antiparasitic_record.pk)
        self.assertEqual(updated_record.date, datetime.date(2025, 2, 1))
        self.assertEqual(updated_record.manufacturer, 'Updated Manufacturer')
        self.assertIsNone(updated_record.time)
        self.assertFalse(updated_record.dosage)

    def test_edit_view_post_invalid_date(self):
        """Test that invalid date is handled correctly"""
        url = reverse('treatment-record-edit', kwargs={'pk': self.treatment_record.pk})
        data = {
            'medication': self.treatment_record.medication.id,
            'date': 'invalid-date',  # Invalid date format
            'time': '11:30',
            'valid_until': '2026-02-01',
            'manufacturer': 'Updated Manufacturer',
            'dosage': '20mg'
        }
        
        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.owner)
        
        response = TreatmentRecordEditView.as_view()(request, pk=self.treatment_record.pk)
        self.assertEqual(response.status_code, 200)  # Should return to form
        # Form should contain error message
        self.assertContains(response, "Enter a valid date")
