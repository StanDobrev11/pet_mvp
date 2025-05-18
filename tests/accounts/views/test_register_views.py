from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from pet_mvp.accounts.views import BaseUserRegisterView, RegisterOwnerView, ClinicRegistrationView
from pet_mvp.accounts.forms import OwnerCreationForm, ClinicRegistrationForm
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import PetAccessCode

UserModel = get_user_model()

class BaseUserRegisterViewTests(TestCase):
    """
    Tests for the BaseUserRegisterView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a user that is already registered
        self.existing_user = UserModel.objects.create_owner(
            email='existing@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        # Create a soft-deleted user
        self.soft_deleted_user = UserModel.objects.create_owner(
            email='deleted@example.com',
            password='testpass123',
            first_name='Deleted',
            last_name='User',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )
        self.soft_deleted_user.is_active = False
        self.soft_deleted_user.save()

    def setup_request(self, request):
        """Helper method to set up request with session and messages."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_dispatch_authenticated_user(self):
        """Test that authenticated users are redirected."""
        url = reverse('register')
        request = self.factory.get(url)
        request.user = self.existing_user

        request = self.setup_request(request)

        view = RegisterOwnerView()
        view.request = request
        view.setup(request)

        response = view.dispatch(request)

        # Should redirect to success URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, view.get_success_url())

    def test_form_valid(self):
        """Test form_valid method."""
        url = reverse('register')
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        request = self.factory.post(url, data=form_data)
        request = self.setup_request(request)

        view = RegisterOwnerView()
        view.request = request
        view.setup(request)

        form = OwnerCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)

        # Should redirect to success URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, view.get_success_url())

        # User should be created
        self.assertTrue(UserModel.objects.filter(email='newuser@example.com').exists())

    def test_activate_soft_deleted_user(self):
        """Test activating a soft-deleted user."""
        url = reverse('register')
        form_data = {
            'email': 'deleted@example.com',  # Email of soft-deleted user
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'Reactivated',
            'last_name': 'User',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        request = self.factory.post(url, data=form_data)
        request = self.setup_request(request)

        view = RegisterOwnerView()
        view.request = request
        view.setup(request)

        form = OwnerCreationForm(data=form_data)
        # Form will be invalid due to unique email constraint
        self.assertFalse(form.is_valid())

        # But the activate_soft_deleted_user method should handle this
        reactivated = view.activate_soft_deleted_user(form)
        self.assertTrue(reactivated)

        # User should be reactivated
        reactivated_user = UserModel.objects.get(email='deleted@example.com')
        self.assertTrue(reactivated_user.is_active)
        self.assertEqual(reactivated_user.first_name, 'Reactivated')
        self.assertEqual(reactivated_user.last_name, 'User')


class RegisterOwnerViewTests(TestCase):
    """
    Tests for the RegisterOwnerView.
    """

    def test_get_request(self):
        """Test GET request to the view."""
        url = reverse('register')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIsInstance(response.context['form'], OwnerCreationForm)

    def test_post_valid_data(self):
        """Test POST request with valid data."""
        url = reverse('register')
        form_data = {
            'email': 'newowner@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'Owner',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to success URL
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)

        # User should be created
        self.assertTrue(UserModel.objects.filter(email='newowner@example.com').exists())

        # User should be logged in
        user = UserModel.objects.get(email='newowner@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


class ClinicRegistrationViewTests(TestCase):
    """
    Tests for the ClinicRegistrationView.
    """

    def setUp(self):
        """Set up test data."""
        # Create a pet with access code
        self.pet = Pet.objects.create(
            name='Test Pet',
            species='Dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )
        self.access_code = PetAccessCode.objects.create(
            pet=self.pet,
            code='TEST123',
            expires_at='2099-01-01 00:00:00'  # Far future date
        )

    def test_get_request(self):
        """Test GET request to the view."""
        url = reverse('clinic-register') + '?email=clinic@example.com&code=TEST123'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/clinc-register.html')
        self.assertIsInstance(response.context['form'], ClinicRegistrationForm)

        # Email should be pre-filled
        self.assertEqual(response.context['form'].initial['email'], 'clinic@example.com')

        # Access code should be in context
        self.assertEqual(response.context['code'], 'TEST123')

    def test_post_valid_data(self):
        """Test POST request with valid data."""
        url = reverse('clinic-register') + '?email=clinic@example.com&code=TEST123'
        form_data = {
            'email': 'clinic@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'clinic_name': 'Test Clinic',
            'clinic_address': '123 Test Street',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to pet details page
        self.assertRedirects(response, reverse('pet-details', kwargs={'pk': self.pet.pk}), fetch_redirect_response=False)

        # User should be created
        self.assertTrue(UserModel.objects.filter(email='clinic@example.com').exists())

        # User should be logged in
        user = UserModel.objects.get(email='clinic@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # Access code should be in session
        self.assertEqual(self.client.session['code'], 'TEST123')
