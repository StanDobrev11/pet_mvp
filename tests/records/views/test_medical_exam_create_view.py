import datetime

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.urls import reverse

from pet_mvp.access_codes.utils import generate_access_code
from pet_mvp.drugs.models import Vaccine, Drug, UrineTest
from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import MedicalExaminationRecordForm, UrineTestForm
from pet_mvp.records.models import MedicalExaminationRecord, VaccinationRecord, MedicationRecord
from pet_mvp.records.views import MedicalExaminationReportCreateView

UserModel = get_user_model()

class MedicalExaminationReportCreateViewTest(TestCase):
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

        self.access_code = generate_access_code(self.pet)

        self.vaccine = Vaccine.objects.create(
            name='Test Vaccine',
            suitable_for='dog',  # MUST match pet.species.lower()
            notes='Test vaccine description'
        )

        self.drug = Drug.objects.create(
            name='Test Drug',
            suitable_for='dog',  # MUST match pet.species.lower()
            notes='Test drug description'
        )

    def setup_request(self, request, user=None):
        request.user = user or self.clinic
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_get_context_data(self):
        """Test that the view adds the correct context data"""
        url = reverse('exam-add')
        request = self.factory.get(f"{url}?source=test&id={self.pet.id}")
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        context = view.get_context_data()

        # Assert context contains expected data
        self.assertEqual(context['pet'], self.pet)
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
            'id': self.pet.id,
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

        request = self.factory.post(f"{url}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

        # Check that a record was created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        record = MedicalExaminationRecord.objects.first()
        self.assertEqual(record.pet, self.pet)
        self.assertEqual(record.doctor, 'Dr. Test')
        self.assertEqual(record.exam_type, 'primary')

    def test_form_valid_with_vaccines(self):
        url = reverse('exam-add')
        post_data = {
            'id': self.pet.id,
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',
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
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(url, data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Patch get_pet to return self.pet
        view.get_pet = lambda: self.pet

        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(VaccinationRecord.objects.count(), 1)

        record = MedicalExaminationRecord.objects.first()
        vaccine_record = VaccinationRecord.objects.first()
        self.assertEqual(vaccine_record.pet, self.pet)
        self.assertEqual(list(record.vaccinations.all()), [vaccine_record])

    def test_form_valid_with_treatments(self):
        url = reverse('exam-add')
        post_data = {
            'id': self.pet.id,
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'General examination',
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
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

        request = self.factory.post(url, data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Patch get_pet to return self.pet
        view.get_pet = lambda: self.pet

        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(MedicationRecord.objects.count(), 1)

        record = MedicalExaminationRecord.objects.first()
        treatment_record = MedicationRecord.objects.first()
        self.assertEqual(treatment_record.pet, self.pet)
        self.assertEqual(list(record.medications.all()), [treatment_record])

    def test_form_valid_with_tests(self):
        """Test form submission with blood, urine and fecal tests"""
        url = reverse('exam-add')

        # Create post data for examination with tests
        post_data = {
            'id': self.pet.id,
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

            # Urine test data
            'has_urine_test': 'True',
            'date_conducted': datetime.date.today().strftime('%Y-%m-%d'),
            'result': 'Normal',
            'color': 'Yellow',
            'clarity': 'Clear',
            'ph': '7.0',
            'specific_gravity': '1.020',
            'protein': 'Negative',
            'glucose': 'Negative',
            'white_blood_cells': '0-2',
            'red_blood_cells': '0-2',
            'additional_notes': 'Urine test notes',
        }

        request = self.factory.post(f"{url}", data=post_data)
        request = self.setup_request(request)

        view = MedicalExaminationReportCreateView()
        view.request = request
        view.kwargs = {}

        # Get the form
        form = MedicalExaminationRecordForm(post_data)
        self.assertTrue(form.is_valid())

        # Check urine test form
        urine_test_form = UrineTestForm(post_data)
        if not urine_test_form.is_valid():
            print("Urine test form errors:", urine_test_form.errors)


        # Call form_valid and check redirect
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that records were created
        self.assertEqual(MedicalExaminationRecord.objects.count(), 1)
        self.assertEqual(UrineTest.objects.count(), 1)


        # Check relationships
        examination = MedicalExaminationRecord.objects.first()
        urine_test = UrineTest.objects.first()


        self.assertEqual(examination.urine_test, urine_test)


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
        """Test form submission with invalid data returns to form with error messages."""
        url = reverse('exam-add')
        post_data = {
            'id': self.pet.id,
            'reason_for_visit': 'Annual checkup',  # Missing required fields like exam_type, doctor
            'vaccines-TOTAL_FORMS': '0',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(url, data=post_data)
        request = self.setup_request(request)

        # Call the view with the request
        response = MedicalExaminationReportCreateView.as_view()(request)

        # Should render the form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please correct the errors in the form.")

        # Should not create any records
        self.assertEqual(MedicalExaminationRecord.objects.count(), 0)

    def test_form_invalid_with_invalid_vaccine_formset(self):
        """Test that view correctly handles an invalid vaccine formset."""
        url = reverse('exam-add')

        post_data = {
            'id': self.pet.id,
            'exam_type': 'primary',
            'date_of_entry': datetime.date.today().strftime('%Y-%m-%d'),
            'doctor': 'Dr. Test',
            'reason_for_visit': 'Annual checkup',
            'treatment_performed': 'Check',

            'vaccines-TOTAL_FORMS': '1',
            'vaccines-INITIAL_FORMS': '0',
            'vaccines-MIN_NUM_FORMS': '0',
            'vaccines-MAX_NUM_FORMS': '1000',
            'vaccines-0-vaccine': '',  # Required field missing to cause formset invalid
            'vaccines-0-batch_number': '',
            'vaccines-0-valid_until': datetime.date.today().strftime('%Y-%m-%d'),
            'treatments-TOTAL_FORMS': '0',
            'treatments-INITIAL_FORMS': '0',
            'treatments-MIN_NUM_FORMS': '0',
            'treatments-MAX_NUM_FORMS': '1000',
        }

        request = self.factory.post(url, data=post_data)
        request = self.setup_request(request)

        response = MedicalExaminationReportCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vaccine information contains errors.")
        self.assertEqual(MedicalExaminationRecord.objects.count(), 0)