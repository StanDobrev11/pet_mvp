from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from pet_mvp.accounts.views import BaseLoginView, LoginOwnerView, PasswordEntryView, AccessCodeEmailView
from pet_mvp.accounts.forms import AccessCodeEmailForm
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import PetAccessCode

import uuid

UserModel = get_user_model()

class BaseLoginViewTests(TestCase):
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

    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': self.user.email,  # AuthenticationForm expects 'username' field
            'password': 'testpass123'
        }, follow=True)  # Follow redirects

        # print("Response status code:", response.status_code)
        # print("Response redirect chain:", response.redirect_chain)
        # print("Response context user:", response.context['user'])
        # print("Response context user is authenticated:", response.context['user'].is_authenticated)
        # print("Response context user pk:", response.context['user'].pk if hasattr(response.context['user'], 'pk') else None)
        # print("Test user pk:", self.user.pk)
        # print("Session keys:", self.client.session.keys())

        # Final response should be 200 OK (dashboard or redirect target)
        self.assertEqual(response.status_code, 200)

        # User should be logged in
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].pk, self.user.pk)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': self.user.email,  # AuthenticationForm expects 'username' field
            'password': 'wrongpassword'
        })
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Should have error message
        self.assertContains(response, 'Invalid email or password')

        # User should not be logged in
        self.assertNotIn('_auth_user_id', self.client.session)


class PasswordEntryViewTests(TestCase):
    """
    Tests for the PasswordEntryView.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create a user
        self.user = UserModel.objects.create_clinic(
            email='clinic@example.com',
            password='testpass123',
            clinic_name='Test Clinic',
            clinic_address='123 Test Street',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        # Create a pet with access code, using a unique passport number
        unique_passport = f'BG01VP{uuid.uuid4().hex[:6].upper()}'
        self.pet = Pet.objects.create(
            name='Test Pet',
            species='Dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number=unique_passport,
        )
        self.access_code = PetAccessCode.objects.create(
            pet=self.pet,
            code='TEST123',
            expires_at='2099-01-01 00:00:00'  # Far future date
        )

    def setup_request(self, request):
        """Helper method to set up request with session and messages."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_get_request(self):
        """Test GET request to the view."""
        url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_entry.html')

        # Email should be pre-filled
        self.assertEqual(response.context['form'].initial['username'], 'clinic@example.com')

    def test_form_valid(self):
        """Test form_valid method."""
        url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        form_data = {
            'username': 'clinic@example.com',
            'password': 'testpass123'
        }
        request = self.factory.post(url, data=form_data)
        request = self.setup_request(request)

        view = PasswordEntryView()
        view.request = request
        view.setup(request)

        # Manually create and validate the form
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, data=form_data)
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)

        # Should redirect to pet details page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pet-details', kwargs={'pk': self.pet.pk}))

        # Access code should be in session
        self.assertEqual(request.session['code'], 'TEST123')

    def test_get_initial(self):
        """Test get_initial method."""
        url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        request = self.factory.get(url)

        view = PasswordEntryView()
        view.request = request

        initial = view.get_initial()
        self.assertEqual(initial['username'], 'clinic@example.com')

    def test_get_form_kwargs(self):
        """Test get_form_kwargs method."""
        url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        form_data = {
            'password': 'testpass123'
            # Intentionally omitting username to test it gets added from GET params
        }
        request = self.factory.post(url, data=form_data)

        view = PasswordEntryView()
        view.request = request

        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs['data']['username'], 'clinic@example.com')


class AccessCodeEmailViewTests(TestCase):
    """
    Tests for the AccessCodeEmailView.
    """

    def setUp(self):
        """Set up test data."""
        # Create a user
        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.clinic = UserModel.objects.create_clinic(
            email='clinic@example.com',
            password='testpass123',
            clinic_name='Test Clinic',
            clinic_address='123 Test Street',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        # Create a pet with access code, using a unique passport number
        unique_passport = f'BG01VP{uuid.uuid4().hex[:6].upper()}'
        self.pet = Pet.objects.create(
            name='Test Pet',
            species='Dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number=unique_passport,
        )
        self.access_code = PetAccessCode.objects.create(
            pet=self.pet,
            code='TEST123',
            expires_at='2099-01-01 00:00:00'  # Far future date
        )

    def test_get_request(self):
        """Test GET request to the view."""
        url = reverse('clinic-login')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/access_code_email.html')
        self.assertIsInstance(response.context['form'], AccessCodeEmailForm)

    def test_form_valid_existing_clinic(self):
        """Test form_valid with existing clinic user."""
        url = reverse('clinic-login')
        form_data = {
            'access_code': 'TEST123',
            'email': 'clinic@example.com'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to password entry page
        expected_url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_form_valid_existing_owner(self):
        """Test form_valid with existing owner user."""
        url = reverse('clinic-login')
        form_data = {
            'access_code': 'TEST123',
            'email': 'owner@example.com'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to index with error message
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)

    def test_form_valid_new_email(self):
        """Test form_valid with new email."""
        url = reverse('clinic-login')
        form_data = {
            'access_code': 'TEST123',
            'email': 'new@example.com'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to clinic registration page
        expected_url = reverse('clinic-register') + '?email=new@example.com&code=TEST123'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_form_invalid(self):
        """Test form_invalid method."""
        url = reverse('clinic-login')
        form_data = {
            'access_code': 'INVALID',  # Invalid access code
            'email': 'clinic@example.com'
        }
        response = self.client.post(url, data=form_data)

        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/access_code_email.html')

        # Should have form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('access_code', response.context['form'].errors)
