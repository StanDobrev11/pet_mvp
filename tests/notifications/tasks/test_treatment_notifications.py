from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from pet_mvp.notifications.tasks import send_treatment_expiration_notifications
from pet_mvp.records.models import MedicationRecord
from pet_mvp.pets.models import Pet
from pet_mvp.drugs.models import Drug
from django.contrib.auth import get_user_model

User = get_user_model()


class TreatmentNotificationTestCase(TestCase):
    """Test cases for treatment expiration notifications."""

    def setUp(self):
        """Set up test data."""
        self.test_user = User.objects.create_owner(
            email='treatment@example.com',
            password='testpassword',
            first_name='Treaty',
            last_name='McTreatface',
            phone_number='1234567890',
            city='Testville',
            country='Testland',
            is_owner=True,
        )

        self.test_pet = Pet.objects.create(
            name='TreatyPet',
            species='Cat',
            breed='Siamese',
            sex='female',
            date_of_birth=timezone.now().date() - timedelta(days=500), 
            color='Grey',
            features='Testing treatment',
            current_weight=5.0,
            passport_number='TREAT123456',
        )
        self.test_pet.owners.add(self.test_user)

        self.test_treatment = Drug.objects.create(
            name='TestTreatment',
            notes='Treatment for testing',
        )

        self.today = timezone.now().date()

        # Record expiring in 7 days
        self.record_7d = MedicationRecord.objects.create(
            manufacturer='Test Manufacturer',
            date=self.today - timedelta(days=5),
            valid_until=self.today + timedelta(days=7),
            pet=self.test_pet,
            medication=self.test_treatment
        )

        # Record expiring in 1 day
        self.record_1d = MedicationRecord.objects.create(
            manufacturer='Test Manufacturer',
            date=self.today - timedelta(days=5),
            valid_until=self.today + timedelta(days=1),
            pet=self.test_pet,
            medication=self.test_treatment
        )

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_treatment_expiration_notifications(self, mock_send_email):
        """Test that notifications are sent for treatments expiring soon."""
        result = send_treatment_expiration_notifications()

        self.assertIn("Processed 2 treatment expiration notifications", result)
        self.assertEqual(mock_send_email.delay.call_count, 2)

        calls = mock_send_email.delay.call_args_list
        time_left_values = [kwargs['context']['time_left'] for args, kwargs in calls]

        self.assertIn("in 1 week", time_left_values)
        self.assertIn("tomorrow", time_left_values)

    def test_manual_task_run(self):
        """Manual test run for treatment notifications."""
        result = send_treatment_expiration_notifications()
        self.assertIn("Processed", result)
        print(f"\nManual task result: {result}")
