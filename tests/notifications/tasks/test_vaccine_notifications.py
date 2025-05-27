"""
Test cases for vaccine expiration notifications.

This module contains tests for the send_vaccine_expiration_notifications task.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from pet_mvp.notifications.tasks import send_vaccine_expiration_notifications
from pet_mvp.records.models import VaccinationRecord
from pet_mvp.pets.models import Pet
from pet_mvp.drugs.models import Vaccine
from django.contrib.auth import get_user_model

User = get_user_model()


class VaccineNotificationTestCase(TestCase):
    """Test cases for vaccine expiration notifications."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.test_user = User.objects.create_owner(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
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
            features='Test pet for vaccine notifications',
            current_weight=10.0,
            passport_number='TEST12345678',
        )
        self.test_pet.owners.add(self.test_user)

        # Create a test vaccine
        self.test_vaccine = Vaccine.objects.create(
            name='TestVaccine',
            notes='Test vaccine for notifications',
        )

        # Create test vaccination records with different expiration dates
        self.today = timezone.now().date()

        # Record expiring in 4 weeks
        self.record_4w = VaccinationRecord.objects.create(
            batch_number='TEST-4W',
            manufacturer='Test Manufacturer',
            manufacture_date=self.today - timedelta(days=30),
            date_of_vaccination=self.today - timedelta(days=7),
            valid_from=self.today - timedelta(days=7),
            valid_until=self.today + timedelta(days=28),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

        # Record expiring in 2 weeks
        self.record_2w = VaccinationRecord.objects.create(
            batch_number='TEST-2W',
            manufacturer='Test Manufacturer',
            manufacture_date=self.today - timedelta(days=30),
            date_of_vaccination=self.today - timedelta(days=7),
            valid_from=self.today - timedelta(days=7),
            valid_until=self.today + timedelta(days=14),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

        # Record expiring in 1 week
        self.record_1w = VaccinationRecord.objects.create(
            batch_number='TEST-1W',
            manufacturer='Test Manufacturer',
            manufacture_date=self.today - timedelta(days=30),
            date_of_vaccination=self.today - timedelta(days=7),
            valid_from=self.today - timedelta(days=7),
            valid_until=self.today + timedelta(days=7),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

        # Record expiring today
        self.record_tomorrow = VaccinationRecord.objects.create(
            batch_number='TEST-TOMORROW',
            manufacturer='Test Manufacturer',
            manufacture_date=self.today - timedelta(days=30),
            date_of_vaccination=self.today - timedelta(days=7),
            valid_from=self.today - timedelta(days=7),
            valid_until=self.today + timedelta(days=1),
            pet=self.test_pet,
            vaccine=self.test_vaccine
        )

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_vaccine_expiration_notifications(self, mock_send_email):
        """Test that notifications are sent for vaccines expiring at different intervals."""
        # Run the task
        result = send_vaccine_expiration_notifications()

        # Check that the task processed 4 notifications (one for each record)
        self.assertIn("Processed 4 vaccine expiration notifications", result)

        # Check that send_template_email_async was called 4 times (once for each record)
        self.assertEqual(mock_send_email.delay.call_count, 4)

        # Check the calls to send_template_email_async
        calls = mock_send_email.delay.call_args_list

        # Extract the time_left values from each call
        time_left_values = []
        for call in calls:
            args, kwargs = call
            time_left_values.append(kwargs['context']['time_left'])

        # Check that we have one notification for each time interval
        self.assertIn("in 4 weeks", time_left_values)
        self.assertIn("in 2 weeks", time_left_values)
        self.assertIn("in 1 week", time_left_values)
        self.assertIn("tomorrow", time_left_values)

    def test_run_task_manually(self):
        """Test running the task manually (for demonstration purposes)."""
        # This test actually runs the task without mocking
        # It's useful for manual testing but might be skipped in automated tests
        result = send_vaccine_expiration_notifications()
        self.assertIn("Processed", result)

        # Print the result for manual verification
        print(f"\nTask result: {result}")
