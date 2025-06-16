"""
Test cases for wrong vaccination report notifications.

This module contains tests for the send_wrong_vaccination_report task.
"""
from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from pet_mvp import settings
from pet_mvp.notifications.tasks import send_wrong_vaccination_report
from pet_mvp.records.models import VaccinationRecord
from pet_mvp.pets.models import Pet
from pet_mvp.drugs.models import Vaccine
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(ADMIN_EMAIL='admin@test.com')
class WrongVaccinationReportTestCase(TestCase):
    """Test cases for wrong vaccination report notifications."""

    def setUp(self):
        """Set up test data."""
        # Create test owner
        self.owner = User.objects.create_owner(
            email='owner@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Owner',
            phone_number='1234567890',
            city='Test City',
            country='Test Country',
            is_owner=True,
        )

        # Create test pet
        self.pet = Pet.objects.create(
            name='TestPet',
            species='Dog',
            breed='Mixed',
            sex='male',
            date_of_birth=timezone.now().date() - timedelta(days=365),
            color='Brown',
            features='Test pet for wrong vaccination reports',
            current_weight=10.0,
            passport_number='TEST12345678',
        )
        self.pet.owners.add(self.owner)

        # Create test vaccine
        self.vaccine = Vaccine.objects.create(
            name='TestVaccine',
            notes='Test vaccine for wrong reports',
        )

        # Create test vaccination record
        self.vacc_record = VaccinationRecord.objects.create(
            batch_number='TEST-WRONG',
            manufacturer='Test Manufacturer',
            manufacture_date=timezone.now().date() - timedelta(days=30),
            date_of_vaccination=timezone.now().date() - timedelta(days=7),
            valid_from=timezone.now().date() - timedelta(days=7),
            valid_until=timezone.now().date() + timedelta(days=358),
            pet=self.pet,
            vaccine=self.vaccine
        )

        # Example reset URL
        self.reset_url = 'http://testserver/records/vaccine/reset/abc123/'

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_wrong_vaccination_report_valid(self, mock_send_email):
        """Test that the report email is sent correctly for a valid vaccine record."""
        result = send_wrong_vaccination_report(self.owner.id, self.vacc_record.id, self.reset_url)

        self.assertEqual(result, "Processed vaccine reset")
        mock_send_email.assert_called_once()

        # Check email call parameters
        args, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs['to_email'], settings.ADMIN_EMAIL)
        self.assertEqual(kwargs['subject'], "Vaccine reset request")
        self.assertEqual(kwargs['template_name'], 'emails/vaccine_reset_request_email.html')

        context = kwargs['context']
        self.assertEqual(context['owner_name'], f"{self.owner.owner.first_name} {self.owner.owner.last_name}")
        self.assertEqual(context['vaccine_name'], self.vaccine.name)
        self.assertEqual(context['url'], self.reset_url)

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_wrong_vaccination_report_invalid_user_or_vaccine(self, mock_send_email):
        """Test that the task raises exceptions for invalid user or record IDs."""
        with self.assertRaises(User.DoesNotExist):
            send_wrong_vaccination_report(999, self.vacc_record.id, self.reset_url)

        with self.assertRaises(VaccinationRecord.DoesNotExist):
            send_wrong_vaccination_report(self.owner.id, 999, self.reset_url)

        mock_send_email.assert_not_called()

    def test_run_task_manually(self):
        """Test running the task manually without mocking (for debugging)."""
        result = send_wrong_vaccination_report(self.owner.id, self.vacc_record.id, self.reset_url)
        self.assertEqual(result, "Processed vaccine reset")
        print(f"\nTask result: {result}")
