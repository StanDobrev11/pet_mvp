from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from pet_mvp.accounts.views import PasswordEntryView
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
        }, follow=True)  # Follow redirects

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Should have error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid email or password" in str(m) for m in messages))

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
        url = reverse('password-entry') + \
            '?email=clinic@example.com&code=TEST123'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_entry.html')

        # Email should be pre-filled
        self.assertEqual(
            response.context['form'].initial['username'], 'clinic@example.com')

    def test_form_valid(self):
        """Test form_valid method."""
        url = reverse('password-entry') + \
            '?email=clinic@example.com&code=TEST123'
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
        self.assertEqual(response.url, reverse(
            'pet-details', kwargs={'pk': self.pet.pk}))

        # Access code should be in session
        self.assertEqual(request.session['code'], 'TEST123')

    def test_get_initial(self):
        """Test get_initial method."""
        url = reverse('password-entry') + \
            '?email=clinic@example.com&code=TEST123'
        request = self.factory.get(url)

        view = PasswordEntryView()
        view.request = request

        initial = view.get_initial()
        self.assertEqual(initial['username'], 'clinic@example.com')

    def test_get_form_kwargs(self):
        """Test get_form_kwargs method."""
        url = reverse('password-entry') + \
            '?email=clinic@example.com&code=TEST123'
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
    def setUp(self):
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
            country='Bulgaria',
            is_active=True,
            is_approved=True,
        )

        self.inactive_clinic = UserModel.objects.create_clinic(
            email='inactive@example.com',
            password='testpass123',
            clinic_name='Inactive Clinic',
            clinic_address='Nowhere',
            phone_number='0887000000',
            city='Plovdiv',
            country='Bulgaria',
            is_active=False,
            is_approved=True,
        )

        self.unapproved_clinic = UserModel.objects.create_clinic(
            email='unapproved@example.com',
            password='testpass123',
            clinic_name='Unapproved Clinic',
            clinic_address='Unknown',
            phone_number='0887111111',
            city='Varna',
            country='Bulgaria',
            is_active=False,
            is_approved=False
        )

        self.pet = Pet.objects.create(
            name='Test Pet',
            species='Dog',
            breed='Shepherd',
            color='Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number=f'BG01VP{uuid.uuid4().hex[:6].upper()}',
        )
        self.pet.owners.add(self.owner)

        self.access_code = PetAccessCode.objects.create(
            pet=self.pet,
            code='TEST123',
            expires_at='2099-01-01 00:00:00'
        )

    def post_data(self, email, code='TEST123'):
        return self.client.post(reverse('clinic-login'), data={'access_code': code, 'email': email})

    def test_get_request(self):
        response = self.client.get(reverse('clinic-login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/access_code_email.html')
        self.assertIsInstance(response.context['form'], AccessCodeEmailForm)

    def test_form_valid_existing_clinic(self):
        response = self.post_data('clinic@example.com')
        expected_url = reverse('password-entry') + '?email=clinic@example.com&code=TEST123'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_form_valid_existing_owner(self):
        response = self.post_data('owner@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/access_code_email.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Owners cannot access" in str(m) for m in messages))

    def test_form_valid_new_email(self):
        response = self.post_data('new@example.com')
        expected_url = reverse('clinic-register') + '?email=new@example.com&code=TEST123'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not in the system" in str(m) for m in messages))

    def test_form_invalid_access_code(self):
        response = self.post_data('clinic@example.com', code='INVALID')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/access_code_email.html')
        self.assertFalse(response.context['form'].is_valid())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please correct the errors below" in str(m) for m in messages))

    def test_unapproved_clinic_redirects_with_email_sent(self):
        response = self.post_data('unapproved@example.com')
        self.assertRedirects(response, reverse('clinic-login'), fetch_redirect_response=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("awaiting approval" in str(m) for m in messages))

    def test_inactive_clinic_activation_email_sent(self):
        response = self.post_data('inactive@example.com')
        self.assertRedirects(response, reverse('clinic-login'), fetch_redirect_response=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Activation email sent" in str(m) for m in messages))


class OwnerDetailsViewTests(TestCase):
    """
    Tests for the OwnerDetailsView.
    """

    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = UserModel.objects.create_owner(
            email='owner2@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

    def test_owner_details_view(self):
        """Test owner details view."""
        url = reverse('owner-details', kwargs={'pk': self.user.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/owner_details.html')
        self.assertContains(response, self.user.owner.first_name)
        self.assertContains(response, self.user.email)


class OwnerEditViewTests(TestCase):
    """
    Tests for the OwnerEditView.
    """

    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = UserModel.objects.create_owner(
            email='owner3@example.com',
            password='testpass123',
            first_name='Edit',
            last_name='Me',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

    def test_owner_edit_view(self):
        """Test owner edit view."""
        url = reverse('owner-edit', kwargs={'pk': self.user.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/owner_edit.html')

        # Test post
        response = self.client.post(url, {
            'first_name': 'Edited',
            'last_name': 'Me',
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'city': self.user.city,
            'country': self.user.country,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Edited')
        self.assertTemplateUsed(response, 'accounts/owner_details.html')
