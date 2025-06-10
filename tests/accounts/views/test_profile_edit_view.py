from django.test import TestCase
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class BaseEditProfileViewTests(TestCase):
    """
    Tests for the BaseLoginView.
    """

    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

