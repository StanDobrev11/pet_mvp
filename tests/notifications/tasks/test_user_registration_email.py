"""
Test cases for user registration email notifications.

This module contains tests for the send_user_registration_email task.
"""
from django.test import TestCase
from unittest.mock import patch

from pet_mvp.notifications.tasks import send_user_registration_email
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationEmailTestCase(TestCase):
    """Test cases for user registration email notifications."""

    def setUp(self):
        """Set up test data."""
        # Create a test user (owner)
        self.test_user = User.objects.create_owner(
            email='newuser@example.com',
            password='testpassword',
            first_name='New',
            last_name='User',
            phone_number='1234567890',
            city='Test City',
            country='Test Country',
            is_owner=True, 
        )

    @patch('pet_mvp.notifications.email_service.EmailService.send_template_email_async')
    def test_send_user_registration_email(self, mock_send_email):
        """Test that user registration email is sent correctly."""
        # Run the task
        result = send_user_registration_email(self.test_user, 'bg')

        # Check that the task processed the registration
        self.assertIn(f"Sent registration email to {self.test_user.email}", result)

        # Check that send_template_email_async was called once
        self.assertEqual(mock_send_email.delay.call_count, 1)

        # Check the call to send_template_email_async
        call = mock_send_email.delay.call_args
        args, kwargs = call

        # Check that the email was sent to the new user
        self.assertEqual(kwargs['to_email'], self.test_user.email)

        # Check that the subject contains a welcome or registration keyword
        self.assertTrue('welcome' in kwargs['subject'].lower() or 'registration' in kwargs['subject'].lower())

        # Check that the template name is correct
        self.assertEqual(kwargs['template_name'], 'emails/user_registration_email.html')

        # Check that the context contains the expected data
        context = kwargs['context']
        self.assertEqual(context['first_name'], self.test_user.owner.first_name)
        self.assertEqual(context['last_name'], self.test_user.owner.last_name)

    def test_run_task_manually(self):
        """Test running the task manually (for demonstration purposes)."""
        # This test actually runs the task without mocking
        # It's useful for manual testing but might be skipped in automated tests
        result = send_user_registration_email(self.test_user, 'bg')
        self.assertIn("Sent registration email", result)

        # Print the result for manual verification
        print(f"\nTask result: {result}")
