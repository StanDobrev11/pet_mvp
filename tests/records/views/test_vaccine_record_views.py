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
from pet_mvp.records.views import VaccineRecordAddView, VaccineRecordEditView, VaccineWrongReportView, VaccineResetView


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
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        # One created in setup + one new
        self.assertEqual(VaccinationRecord.objects.count(), 2)

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
        vaccine_record = VaccinationRecord.objects.get(
            vaccine=self.rabies_vaccine)
        expected_valid_from = vaccination_date + timedelta(days=21)
        self.assertEqual(vaccine_record.valid_from, expected_valid_from)

    def test_edit_view_get(self):
        """Test the get request for editing a vaccine record"""
        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
        request = self.factory.get(url)
        request = self.setup_request(request, self.clinic)

        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Vaccination Record")
        self.assertContains(response, self.vaccine_record.vaccine.name)

    def test_edit_view_post_valid(self):
        """Test posting valid data to update a vaccine record"""
        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
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
        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Verify the record was updated
        updated_record = VaccinationRecord.objects.get(
            pk=self.vaccine_record.pk)
        self.assertEqual(updated_record.date_of_vaccination, new_date)
        self.assertEqual(updated_record.manufacturer, 'Updated Manufacturer')
        self.assertEqual(updated_record.batch_number, 'NEWBATCH123')

    def test_edit_view_unauthorized(self):
        """Test that non-clinic users cannot edit records"""
        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
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

    def test_edit_view_edit_wrong_vaccine(self):
        """Test editing a vaccine that has been marked as wrong"""
        # Mark vaccine as wrong and editable
        self.vaccine_record.is_wrong = True
        self.vaccine_record.is_editable = True
        self.vaccine_record.save()

        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
        data = {
            'vaccine': self.vaccine_record.vaccine.id,
            'date_of_vaccination': '2025-02-01',
            'valid_until': '2026-02-01',
            'manufacturer': 'Corrected Manufacturer',
            'manufacture_date': '2023-07-01',
            'batch_number': 'CORRECTED123'
        }

        request = self.factory.post(url, data=data)
        # Even owner can edit if marked editable
        request = self.setup_request(request, self.owner)

        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Verify the record was updated
        updated_record = VaccinationRecord.objects.get(
            pk=self.vaccine_record.pk)
        self.assertEqual(updated_record.manufacturer, 'Corrected Manufacturer')
        self.assertEqual(updated_record.batch_number, 'CORRECTED123')
        self.assertFalse(updated_record.is_wrong)  # Should be reset
        self.assertFalse(updated_record.is_editable)  # Should be reset

    def test_edit_view_unapproved_clinic(self):
        """Test that unapproved clinic users cannot edit records"""
        # Create unapproved clinic
        unapproved_clinic = UserModel.objects.create_clinic(
            email='unapproved@test.com',
            password='1234',
            name='Unapproved Clinic',
            address='456 Some Address',
            is_owner=False,
            phone_number='0887142537',
            city='Sofia',
            country='Bulgaria',
            is_approved=False
        )

        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
        request = self.factory.get(url)
        request = self.setup_request(request, unapproved_clinic)

        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 403)  # Should return forbidden

    def test_edit_view_invalid_form_data(self):
        """Test edit view with invalid form data"""
        url = reverse('vaccine-record-edit',
                      kwargs={'pk': self.vaccine_record.pk})
        data = {
            'vaccine': self.vaccine_record.vaccine.id,
            'date_of_vaccination': 'invalid-date',  # Invalid date format
            'valid_until': '2026-02-01',
            'manufacturer': 'Updated Manufacturer',
            'manufacture_date': '2023-07-01',
            'batch_number': 'NEWBATCH123'
        }

        request = self.factory.post(url, data=data)
        request = self.setup_request(request, self.clinic)

        response = VaccineRecordEditView.as_view()(request, pk=self.vaccine_record.pk)
        self.assertEqual(response.status_code, 200)  # Should return to form
        self.assertContains(response, "Enter a valid date")


class VaccineWrongReportAndResetViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()        # Create admin user
        self.admin = UserModel.objects.create_superuser(
            email='admin@test.com',
            password='admin1234',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        # Create clinic user
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

        # Create pet
        self.pet = Pet.objects.create(
            name='Test Dog',
            species='dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )

        # Create owner
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

        # Create a vaccine record
        self.vaccine_record = VaccinationRecord.objects.create(
            pet=self.pet,
            vaccine=self.vaccine,
            date_of_vaccination=make_aware(datetime.datetime(2025, 1, 20)),
            valid_from=make_aware(datetime.datetime(2025, 1, 20)),
            valid_until=make_aware(datetime.datetime(2026, 1, 20)),
            manufacturer='Test Manufacturer',
            manufacture_date=make_aware(datetime.datetime(2023, 6, 10)),
            batch_number='TEST123'
        )

        self.pet.owners.add(self.owner)

    def setup_request(self, request, user):
        """Helper method to setup request with user and messages"""
        request.user = user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_wrong_report_view_post_valid(self):
        """Test submitting a valid wrong vaccination report"""
        url = reverse('wrong-vaccine-report')
        data = {
            'vaccine_id': self.vaccine_record.pk,
        }
        request = self.factory.post(url, data=data)
        request.GET = {}  # Add empty GET data for url building
        request = self.setup_request(request, self.owner)

        response = VaccineWrongReportView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Check vaccine record was marked as wrong
        vaccine = VaccinationRecord.objects.get(pk=self.vaccine_record.pk)
        self.assertTrue(vaccine.is_wrong)

    def test_wrong_report_view_post_duplicate(self):
        """Test submitting a wrong report for an already reported vaccine"""
        # Mark vaccine as already reported
        self.vaccine_record.is_wrong = True
        self.vaccine_record.save()

        url = reverse('wrong-vaccine-report')
        data = {
            'vaccine_id': self.vaccine_record.pk,
        }
        request = self.factory.post(url, data=data)
        request.GET = {}  # Add empty GET data for url building
        request = self.setup_request(request, self.owner)

        response = VaccineWrongReportView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify warning message is set
        messages = list(request._messages)
        self.assertTrue(any('already been submitted' in str(m)
                        for m in messages))

    def test_wrong_report_view_post_missing_id(self):
        """Test submitting a wrong report without a vaccine ID"""
        url = reverse('wrong-vaccine-report')
        request = self.factory.post(url, {})  # Empty data
        request.GET = {}  # Add empty GET data for url building
        request = self.setup_request(request, self.owner)

        response = VaccineWrongReportView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify error message is set
        messages = list(request._messages)
        self.assertTrue(any('Missing vaccine ID' in str(m) for m in messages))

    def test_reset_view_get_unauthorized(self):
        """Test that non-staff users cannot access reset view"""
        url = reverse('vaccine-record-reset', kwargs={
            'uidb64': 'test-uid',
            'token': 'test-token'
        })
        request = self.factory.get(url)
        request = self.setup_request(request, self.owner)

        response = VaccineResetView.as_view()(
            request, uidb64='test-uid', token='test-token')
        self.assertEqual(response.status_code, 403)  # Should be forbidden

    def test_reset_view_get_invalid_token(self):
        """Test reset view with invalid token"""
        url = reverse('vaccine-record-reset', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid'
        })
        request = self.factory.get(url)
        request = self.setup_request(request, self.admin)

        response = VaccineResetView.as_view()(request, uidb64='invalid', token='invalid')
        self.assertEqual(response.status_code, 403)  # Should return forbidden

    def test_reset_view_get_valid(self):
        """Test reset view with valid token"""
        # First mark the vaccine as wrong
        self.vaccine_record.is_wrong = True
        self.vaccine_record.save()

        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(self.vaccine_record.pk))
        token = default_token_generator.make_token(self.admin)

        url = reverse('vaccine-record-reset', kwargs={
            'uidb64': uid,
            'token': token
        })
        request = self.factory.get(url)
        request = self.setup_request(request, self.admin)

        response = VaccineResetView.as_view()(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Check vaccine record was marked as editable
        vaccine = VaccinationRecord.objects.get(pk=self.vaccine_record.pk)
        self.assertTrue(vaccine.is_editable)

        # Verify success message is set
        messages = list(request._messages)
        self.assertTrue(any('can now be edited' in str(m) for m in messages))
