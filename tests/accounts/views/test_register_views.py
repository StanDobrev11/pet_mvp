from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from pet_mvp.accounts.views import RegisterOwnerView
from pet_mvp.accounts.forms import OwnerCreateForm, ClinicRegistrationForm
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

        form = OwnerCreateForm(data=form_data)
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

        form = OwnerCreateForm(data=form_data)
        # Form will be invalid due to unique email constraint
        self.assertFalse(form.is_valid())

        # But the activate_soft_deleted_user method should handle this
        reactivated = view.activate_soft_deleted_user(form)
        self.assertTrue(reactivated)

        # User should be reactivated
        reactivated_user = UserModel.objects.get(email='deleted@example.com')
        reactivated_user.owner.refresh_from_db()
        self.assertTrue(reactivated_user.is_active)
        self.assertEqual(reactivated_user.owner.first_name, 'Reactivated')
        self.assertEqual(reactivated_user.owner.last_name, 'User')


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
        self.assertIsInstance(response.context['form'], OwnerCreateForm)

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


    def test_phone_number_invalid(self):
        url = reverse('register')
        form_data = {
            'email': 'newowner@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'Owner',
            'phone_number': '088722333654321', # wrong phone number
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        response = self.client.post(url, data=form_data)

        # Should load same form
        self.assertEqual(response.status_code, 200)

        # User should not be created
        self.assertFalse(UserModel.objects.filter(email='newowner@example.com').exists())

        # Following error message
        self.assertContains(response, 'Invalid Bulgarian mobile number format.')


    def test_uppercase_email_is_normalized(self):
        """Test that an uppercase email is saved in lowercase."""
        url = reverse('register')
        form_data = {
            'email': 'NEWOWNER@EXAMPLE.COM',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Caps',
            'last_name': 'Lock',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to success URL
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)

        # User should be created with lowercase email
        self.assertTrue(UserModel.objects.filter(email='newowner@example.com').exists())

        # Ensure no user with the original uppercase email
        self.assertFalse(UserModel.objects.filter(email='NEWOWNER@EXAMPLE.COM').exists())

        # Check that the email stored is lowercase
        user = UserModel.objects.get(email='newowner@example.com')
        self.assertEqual(user.email, 'newowner@example.com')

    def test_user_fields_created_correctly(self):
        """Test that all user fields are created correctly from form input."""
        url = reverse('register')
        form_data = {
            'email': 'completeuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '0887123456',
            'city': 'Plovdiv',
            'country': 'Bulgaria'
        }

        response = self.client.post(url, data=form_data)

        # Should redirect after successful registration
        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)

        # Check user exists
        user_exists = UserModel.objects.filter(email='completeuser@example.com').exists()
        self.assertTrue(user_exists)

        # Fetch user and check all fields
        user = UserModel.objects.get(email='completeuser@example.com')
        owner_profile = user.owner  # Assuming there is a related Owner model via OneToOne

        self.assertEqual(user.email, 'completeuser@example.com')
        self.assertTrue(user.check_password('securepass123'))
        self.assertEqual(owner_profile.first_name, 'John')
        self.assertEqual(owner_profile.last_name, 'Doe')
        self.assertEqual(user.phone_number, '00359887123456')
        self.assertEqual(user.city, 'Plovdiv')
        self.assertEqual(user.country, 'Bulgaria')

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
        self.assertTemplateUsed(response, 'accounts/clinic-register.html')
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
            'name': 'Test Clinic',
            'address': '123 Test Street',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        response = self.client.post(url, data=form_data)

        # Should redirect to access code login page
        self.assertRedirects(response, reverse('clinic-login'), fetch_redirect_response=False)

        # User should be created
        self.assertTrue(UserModel.objects.filter(email='clinic@example.com').exists())

        # User should not be logged in
        user = UserModel.objects.get(email='clinic@example.com')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Access code should be in session
        self.assertEqual(self.client.session['code'], 'TEST123')

    def test_clinic_fields_created_correctly(self):
        """Test that all clinic fields are correctly created and normalized."""
        url = reverse('clinic-register') + '?email=CLINIC@EXAMPLE.COM&code=TEST123'
        form_data = {
            'email': 'CLINIC@EXAMPLE.COM',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'name': 'test vet clinic',
            'address': ' 123 Test Street ',
            'phone_number': '0887123456',
            'city': 'sofia',
            'country': 'bulgaria'
        }

        response = self.client.post(url, data=form_data)

        # Check redirect
        self.assertRedirects(response, reverse('clinic-login'), fetch_redirect_response=False)

        # User created
        user = UserModel.objects.get(email='clinic@example.com')  # should be normalized
        self.assertEqual(user.email, 'clinic@example.com')
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password('testpass123'))

        # Check field normalization
        self.assertEqual(user.phone_number, '00359887123456')  # assuming your manager normalizes this
        self.assertEqual(user.city, 'Sofia')
        self.assertEqual(user.country, 'Bulgaria')

        # Clinic profile created
        self.assertTrue(hasattr(user, 'clinic'))
        clinic = user.clinic
        self.assertEqual(clinic.name, 'Test Vet Clinic')  # should be title-cased
        self.assertEqual(clinic.address, '123 Test Street')
