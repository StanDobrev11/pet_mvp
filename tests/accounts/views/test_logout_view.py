from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class LogoutViewTests(TestCase):
    """
    Tests for the logout_view function.
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

        # Log in the user
        self.client.login(username='owner@example.com', password='testpass123')

    def test_logout(self):
        """Test that the logout view logs out the user and redirects to index."""
        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        # Call logout view
        url = reverse('logout')
        response = self.client.get(url)

        # Should redirect to index
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)

        # User should be logged out
        self.assertFalse('_auth_user_id' in self.client.session)
