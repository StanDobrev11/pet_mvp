from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch
from allauth.account.signals import user_signed_up


UserModel = get_user_model()

class SendWelcomeEmailSignalTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('pet_mvp.accounts.signals.send_user_registration_email')
    def test_send_user_registration_email_called_on_signup(self, mock_send_email):
        # Arrange: create a dummy request and user
        request = self.factory.get('/')
        user = UserModel.objects.create_owner(
            email='newuser@example.com',
            password='securepass123',
            first_name='Test',
            last_name='User',
            phone_number='0888888888',
            city='Sofia',
            country='Bulgaria',
            default_language='bg',
        )

        # Act: send the signal
        user_signed_up.send(sender=UserModel, request=request, user=user)

        # Assert: check the Celery task is called with the right arguments
        mock_send_email.assert_called_once_with(user, 'bg')