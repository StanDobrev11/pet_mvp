from django.test import TestCase, RequestFactory
from django.urls import reverse
from datetime import date

from pet_mvp.drugs.models import BloodTest, UrineTest, FecalTest, Vaccine, Drug
from pet_mvp.drugs.views import (
    BaseDetailsView, VaccineDetailsView, DrugDetailsView,
    BloodTestDetailsView, UrineTestDetailsView, FecalTestDetailsView
)
from pet_mvp.records.models import VaccinationRecord, MedicationRecord
from pet_mvp.pets.models import Pet


class BaseDetailsViewTests(TestCase):
    """
    Tests for the BaseDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a test view that inherits from BaseDetailsView
        class TestView(BaseDetailsView):
            template_name = "test_template.html"

        self.view_class = TestView

    def test_get_context_data(self):
        """Test that the context contains the source and id from the request."""
        request = self.factory.get('/?source=test_source&id=123')

        view = self.view_class()
        view.request = request
        view.setup(request)
        view.object = None  # Set object to None to avoid AttributeError

        context = view.get_context_data()

        self.assertIn('source', context)
        self.assertEqual(context['source'], 'test_source')
        self.assertIn('id', context)
        self.assertEqual(context['id'], '123')


class VaccineDetailsViewTests(TestCase):
    """
    Tests for the VaccineDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create test pet and vaccine
        self.test_pet = Pet.objects.create(
            name='TestPet',
            species='Dog',
            breed='Mixed',
            sex='male',
            date_of_birth=date(2022, 1, 1),
            color='Brown',
            features='Test pet for vaccine details',
            current_weight=10.0,
            passport_number='TEST12345678',
        )

        self.test_vaccine = Vaccine.objects.create(
            name='Rabies Vaccine',
            notes='Test vaccine for details view',
        )

        # Create a vaccination record
        self.vaccination_record = VaccinationRecord.objects.create(
            batch_number='TEST-BATCH',
            manufacturer='Test Manufacturer',
            manufacture_date=date(2023, 1, 1),
            date_of_vaccination=date(2023, 5, 15),
            valid_from=date(2023, 5, 15),
            valid_until=date(2024, 5, 15),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

    def test_view_attributes(self):
        """Test the attributes of the VaccineDetailsView."""
        self.assertEqual(VaccineDetailsView.model, VaccinationRecord)
        self.assertEqual(VaccineDetailsView.template_name, "drugs/vaccine_details.html")


class DrugDetailsViewTests(TestCase):
    """
    Tests for the DrugDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create test pet and drug
        self.test_pet = Pet.objects.create(
            name='TestPet',
            species='Dog',
            breed='Mixed',
            sex='male',
            date_of_birth=date(2022, 1, 1),
            color='Brown',
            features='Test pet for medication details',
            current_weight=10.0,
            passport_number='TEST12345678',
        )

        self.test_drug = Drug.objects.create(
            name='Amoxicillin',
            notes='Test drug for details view',
        )

        # Create a medication record
        self.medication_record = MedicationRecord.objects.create(
            manufacturer='Test Manufacturer',
            date=date(2023, 5, 15),
            dosage='10mg twice daily',
            valid_until=date(2023, 6, 15),
            pet=self.test_pet,
            medication=self.test_drug
        )

    def test_view_attributes(self):
        """Test the attributes of the DrugDetailsView."""
        self.assertEqual(DrugDetailsView.model, MedicationRecord)
        self.assertEqual(DrugDetailsView.template_name, "drugs/treatment_details.html")


class BloodTestDetailsViewTests(TestCase):
    """
    Tests for the BloodTestDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a blood test
        self.blood_test = BloodTest.objects.create(
            result="Normal blood count",
            date_conducted=date(2023, 5, 15),
            additional_notes="No abnormalities detected"
        )

    def test_view_attributes(self):
        """Test the attributes of the BloodTestDetailsView."""
        self.assertEqual(BloodTestDetailsView.model, BloodTest)
        self.assertEqual(BloodTestDetailsView.template_name, "drugs/blood_test_details.html")


class UrineTestDetailsViewTests(TestCase):
    """
    Tests for the UrineTestDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a urine test
        self.urine_test = UrineTest.objects.create(
            result="Normal urinalysis",
            date_conducted=date(2023, 5, 15),
            additional_notes="No abnormalities detected"
        )

    def test_view_attributes(self):
        """Test the attributes of the UrineTestDetailsView."""
        self.assertEqual(UrineTestDetailsView.model, UrineTest)
        self.assertEqual(UrineTestDetailsView.template_name, "drugs/urine_test_details.html")


class FecalTestDetailsViewTests(TestCase):
    """
    Tests for the FecalTestDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a fecal test
        self.fecal_test = FecalTest.objects.create(
            result="Normal fecal analysis",
            date_conducted=date(2023, 5, 15),
            additional_notes="No abnormalities detected"
        )

    def test_view_attributes(self):
        """Test the attributes of the FecalTestDetailsView."""
        self.assertEqual(FecalTestDetailsView.model, FecalTest)
        self.assertEqual(FecalTestDetailsView.template_name, "drugs/fecal_test_details.html")
