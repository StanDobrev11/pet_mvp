"""
Test cases for wrong vaccination report notifications.

This module contains tests for the send_wrong_vaccination_report task.
"""
import os
from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

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
        # Create a test owner
        self.test_owner = User.objects.create_owner(
            email='owner@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Owner',
            phone_number='1234567890',
            city='Test City',
            country='Test Country',
            is_owner=True,
        )

        # Create a test pet
        self.test_pet = Pet.objects.create(
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
        self.test_pet.owners.add(self.test_owner)

        # Create a test vaccine
        self.test_vaccine = Vaccine.objects.create(
            name='TestVaccine',
            notes='Test vaccine for wrong reports',
        )

        # Create a test vaccination record
        self.test_record = VaccinationRecord.objects.create(
            batch_number='TEST-WRONG',
            manufacturer='Test Manufacturer',
            manufacture_date=timezone.now().date() - timedelta(days=30),
            date_of_vaccination=timezone.now().date() - timedelta(days=7),
            valid_from=timezone.now().date() - timedelta(days=7),
            valid_until=timezone.now().date() + timedelta(days=358),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

        # Mock reset URL
        self.reset_url = 'http://testserver/reset-vaccine/123/'

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_wrong_vaccination_report(self, mock_send_email):
        """Test that wrong vaccination report email is sent correctly."""
        # Run the task
        result = send_wrong_vaccination_report(
            self.test_owner.id,
            self.test_record.id,
            self.reset_url
        )

        # Check that the task processed the report
        self.assertEqual(result, "Processed vaccine reset")

        # Check that send_template_email_async was called once
        mock_send_email.assert_called_once()

        # Get the call arguments
        args, kwargs = mock_send_email.call_args

        # Verify email is sent to admin
        self.assertEqual(kwargs['to_email'], 'admin@petpal.cloudmachine.uk')

        # Check that the subject indicates a reset request
        self.assertEqual(kwargs['subject'], "Vaccine reset request")

        # Check that the correct template is used
        self.assertEqual(kwargs['template_name'], 'emails/vaccine_reset_request_email.html')

        # Verify context data
        context = kwargs['context']
        self.assertEqual(context['owner_name'], f"{self.test_owner.owner.first_name} {self.test_owner.owner.last_name}")
        self.assertEqual(context['vaccine_name'], self.test_vaccine.name)
        self.assertEqual(context['url'], self.reset_url)

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_wrong_vaccination_report_invalid_ids(self, mock_send_email):
        """Test that task handles invalid IDs appropriately."""
        with self.assertRaises(User.DoesNotExist):
            send_wrong_vaccination_report(999, self.test_record.id, self.reset_url)

        with self.assertRaises(VaccinationRecord.DoesNotExist):
            send_wrong_vaccination_report(self.test_owner.id, 999, self.reset_url)

        # Verify no emails were sent
        mock_send_email.assert_not_called()

    def test_manual_task_run(self):
        """Test running the task manually (for demonstration purposes)."""
        # This test actually runs the task without mocking
        # It's useful for manual testing but might be skipped in automated tests
        result = send_wrong_vaccination_report(
            self.test_owner.id,
            self.test_record.id,
            self.reset_url
        )
        self.assertEqual(result, "Processed vaccine reset")
        print(f"\nTask result: {result}")
