import datetime
from unittest.mock import patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.urls import reverse

from pet_mvp.access_codes.utils import generate_access_code
from pet_mvp.accounts.models import Clinic
from pet_mvp.access_codes.models import PetAccessCode
from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest
from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import MedicalExaminationRecordForm
from pet_mvp.records.models import MedicalExaminationRecord, VaccinationRecord, MedicationRecord
from pet_mvp.records.views import MedicalExaminationReportCreateView


class MedicalExaminationReportCreateViewTest(TestCase):
    def setUp(self):
        # Create mock objects needed for tests
        self.factory = RequestFactory()

        # Create a clinic (user)
        self.clinic = Clinic.objects.create(
            email='test-clinic@test.com',
            password='1234',
            clinic_name='Test Clinic',
            is_owner=False,
            phone_number='0887142536',
            clinic_address='123 Some Address',
            city='Varna',
            country='Bulgaria',
        )

        # Create a pet with access code
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

        self.access_code = generate_access_code(self.pet)

        # Create test data for optional models
        self.vaccine = Vaccine.objects.create(
            name='Test Vaccine',
            description='Test vaccine description'
        )

        self.drug = Drug.objects.create(
            name='Test Drug',
            description='Test drug description'
        )

    def setup_request(self, request, user=None):
        """Helper method to set up request with session and messages"""
        request.user = user or self.clinic
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_get_context_data(self):
        """Test that the view adds the correct context data"""
        url = reverse('exam-add')
        request = self.factory.get(f"{url}?code={self.access_code.code}&source=test")
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        context = view.get_context_data()

        # Assert context contains expected data
        self.assertEqual(context['pet'], self.pet)
        self.assertEqual(context['code'], self.access_code.code)
        self.assertEqual(context['source'], 'test')
        self.assertIsInstance(context['report_form'], MedicalExaminationRecordForm)
        self.assertIn('vaccine_formset', context)
        self.assertIn('treatment_formset', context)
        self.assertIn('blood_test_form', context)
        self.assertIn('urine_test_form', context)
        self.assertIn('fecal_test_form', context)
        self.assertIn('additional_info_fields', context)

    def test_form_valid_basic(self):
        """Test the basic form submission without optional components"""
        url = reverse('exam-add')

        # Create post data for basic examination record
        post_data = {
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',
            # Add management form data for the formsets
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(f"{url}?code={self.access_code.code}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that a record was created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        record = MedicalExaminationRecord.objects.first()
        self.assertEqual(record.pet, self.pet)
        self.assertEqual(record.doctor, 'Dr. Test')
        self.assertEqual(record.exam_type, 'primary')

    def test_form_valid_with_vaccines(self):
        """Test form submission with vaccine records"""
        url = reverse('exam-add')

        # Create post data for examination with vaccines
        post_data = {
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',

            # Vaccine formset data
            'vaccines-TOTAL_FORMS': '1',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'vaccines-0-vaccine': self.vaccine.id,
            'vaccines-0-batch_number': 'BATCH123',
            'vaccines-0-manufacturer': 'TestManufacturer',
            'vaccines-0-manufacture_date': datetime.date.today().strftime('%Y-%m-%d'),
            'vaccines-0-date_of_vaccination': datetime.date.today().strftime('%Y-%m-%d'),
            'vaccines-0-valid_from': datetime.date.today().strftime('%Y-%m-%d'),
            'vaccines-0-valid_until': (datetime.date.today() + datetime.timedelta(days=365)).strftime('%Y-%m-%d'),

            # Treatment formset data
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(f"{url}?code={self.access_code.code}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that records were created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(VaccinationRecord.objects.count(), 1)

        # Check relationships
        examination = MedicalExaminationRecord.objects.first()
        vaccine_record = VaccinationRecord.objects.first()
        self.assertEqual(vaccine_record.pet, self.pet)
        self.assertEqual(list(examination.vaccinations.all()), [vaccine_record])

    def test_form_valid_with_treatments(self):
        """Test form submission with medication records"""
        url = reverse('exam-add')

        # Create post data for examination with treatments
        post_data = {
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',

            # Vaccine formset data
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',

            # Treatment formset data
            'treatments-TOTAL_FORMS': '1',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
            'treatments-0-medication': self.drug.id,
            'treatments-0-manufacturer': 'TestManufacturer',
            'treatments-0-date': datetime.date.today().strftime('%Y-%m-%d'),
            'treatments-0-dosage': '10mg daily',
            'treatments-0-valid_until': (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        }

        request = self.factory.post(f"{url}?code={self.access_code.code}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that records were created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(MedicationRecord.objects.count(), 1)

        # Check relationships
        examination = MedicalExaminationRecord.objects.first()
        medication_record = MedicationRecord.objects.first()
        self.assertEqual(medication_record.pet, self.pet)
        self.assertEqual(list(examination.medications.all()), [medication_record])

    def test_form_valid_with_tests(self):
        """Test form submission with blood, urine and fecal tests"""
        url = reverse('exam-add')

        # Create post data for examination with tests
        post_data = {
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',

            # Formset data
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',

            # Blood test data
            'has_blood_test': 'True',
            'name': 'Complete Blood Count',
            'date_conducted': datetime.date.today().strftime('%Y-%m-%d'),
            'result': 'Normal',
            'white_blood_cells': '10000',
            'red_blood_cells': '5000000',
            'hemoglobin': '15.0',
            'platelets': '200000',
            'additional_notes': 'Everything normal',
        }

        request = self.factory.post(f"{url}?code={self.access_code.code}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that records were created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(BloodTest.objects.count(), 1)

        # Check relationships
        examination = MedicalExaminationRecord.objects.first()
        blood_test = BloodTest.objects.first()
        self.assertEqual(examination.blood_test, blood_test)

    def test_invalid_access_code(self):
        """Test that view returns 404 with invalid access code"""
        url = reverse('exam-add')
        request = self.factory.get(f"{url}?code=INVALID")
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        with self.assertRaises(Exception):  # Should raise 404
            view.get_context_data()

    def test_form_invalid(self):
        """Test behavior with invalid form data"""
        url = reverse('exam-add')

        # Create post data with missing required fields
        post_data = {
            # Missing exam_type, doctor, etc.
            'reason_for_visit': 'Annual checkup',

            # Formset data
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(f"{url}?code={self.access_code.code}", data=post_data)
        request = self.setup_request(request)

        response = MedicalExaminationReportCreateView.as_view()(request)

        # Should not redirect (form invalid)
        self.assertEqual(response.status_code, 200)

        # No records should be created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 0)