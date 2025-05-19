from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from pet_mvp.common.views import IndexView, DashboardView
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class IndexViewTests(TestCase):
    """
    Tests for the IndexView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = UserModel.objects.create_owner(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

    def test_get_unauthenticated(self):
        """Test that unauthenticated users see the index page."""
        request = self.factory.get(reverse('index'))
        # Use AnonymousUser to simulate an unauthenticated user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        response = IndexView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'common/index.html')

    def test_get_authenticated(self):
        """Test that authenticated users are redirected to the dashboard."""
        request = self.factory.get(reverse('index'))
        # Use the actual user object (which is already authenticated)
        request.user = self.user

        response = IndexView.as_view()(request)

        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.url, reverse('dashboard'))


class DashboardViewTests(TestCase):
    """
    Tests for the DashboardView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = UserModel.objects.create_owner(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

        # Create a pet for the user
        self.pet = Pet.objects.create(
            name="Buddy",
            species="Dog",
            breed="Labrador",
            sex="male",
            date_of_birth="2020-01-01",  # Add required date_of_birth field
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )
        self.pet.owners.add(self.user)

    def test_get_context_data(self):
        """Test that the context contains the user's pets."""
        request = self.factory.get(reverse('dashboard'))
        request.user = self.user

        view = DashboardView()
        view.request = request
        view.setup(request)

        context = view.get_context_data()

        self.assertIn('pets', context)
        self.assertEqual(list(context['pets']), [self.pet])

    def test_login_required(self):
        """Test that the view requires login."""
        response = self.client.get(reverse('dashboard'))

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
