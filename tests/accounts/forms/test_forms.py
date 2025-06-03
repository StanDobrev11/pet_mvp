from django.test import TestCase
from django.contrib.auth import get_user_model

from pet_mvp.accounts.forms import OwnerCreateForm, ClinicRegistrationForm, AccessCodeEmailForm
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import PetAccessCode

import uuid

UserModel = get_user_model()


class OwnerCreationFormTests(TestCase):
    """
    Tests for the OwnerCreationForm.
    """

    def test_form_with_valid_data(self):
        """Test that the form is valid with valid data."""
        form_data = {
            'email': 'owner@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Owner',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        form = OwnerCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_mismatched_passwords(self):
        """Test that the form is invalid when passwords don't match."""
        form_data = {
            'email': 'owner@example.com',
            'password1': 'testpass123',
            'password2': 'testpass456',  # Different password
            'first_name': 'Test',
            'last_name': 'Owner',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        form = OwnerCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_with_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing."""
        form_data = {
            'email': 'owner@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            # Missing first_name, last_name, etc.
        }
        form = OwnerCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Check that the non-field error about first_name and last_name is present
        self.assertIn('__all__', form.errors)
        self.assertIn('Owners must have a first name and last name', str(form.errors['__all__']))


class ClinicRegistrationFormTests(TestCase):
    """
    Tests for the ClinicRegistrationForm.
    """

    def test_form_with_valid_data(self):
        """Test that the form is valid with valid data."""
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
        form = ClinicRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_mismatched_passwords(self):
        """Test that the form is invalid when passwords don't match."""
        form_data = {
            'email': 'clinic@example.com',
            'password1': 'testpass123',
            'password2': 'testpass456',  # Different password
            'clinic_name': 'Test Clinic',
            'clinic_address': '123 Test Street',
            'phone_number': '0887654321',
            'city': 'Sofia',
            'country': 'Bulgaria'
        }
        form = ClinicRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_with_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing."""
        form_data = {
            'email': 'clinic@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            # Missing clinic_name, clinic_address, etc.
        }
        form = ClinicRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Check that the non-field error about clinic_name and clinic_address is present
        self.assertIn('__all__', form.errors)
        self.assertIn('Clinics must have a name and address', str(form.errors['__all__']))

    def test_is_owner_set_to_false(self):
        """Test that is_owner is set to False on the instance."""
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
        form = ClinicRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.instance.is_owner)


class AccessCodeEmailFormTests(TestCase):
    """
    Tests for the AccessCodeEmailForm.
    """

    def setUp(self):
        """Set up test data."""
        # Create a pet with a unique passport number for each test
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

        # Create a user
        self.user = UserModel.objects.create_owner(
            email='existing@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

    def test_form_with_valid_data_existing_email(self):
        """Test that the form is valid with valid data and existing email."""
        form_data = {
            'access_code': 'TEST123',
            'email': 'existing@example.com'
        }
        form = AccessCodeEmailForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Check that the email exists flag is set correctly
        email_data = form.cleaned_data.get('email')
        self.assertEqual(email_data['email'], 'existing@example.com')
        self.assertTrue(email_data['exists'])

    def test_form_with_valid_data_new_email(self):
        """Test that the form is valid with valid data and new email."""
        form_data = {
            'access_code': 'TEST123',
            'email': 'new@example.com'
        }
        form = AccessCodeEmailForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Check that the email exists flag is set correctly
        email_data = form.cleaned_data.get('email')
        self.assertEqual(email_data['email'], 'new@example.com')
        self.assertFalse(email_data['exists'])

    def test_form_with_invalid_access_code(self):
        """Test that the form is invalid with an invalid access code."""
        form_data = {
            'access_code': 'INVALID',
            'email': 'existing@example.com'
        }
        form = AccessCodeEmailForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('access_code', form.errors)

    def test_form_with_invalid_email(self):
        """Test that the form is invalid with an invalid email."""
        form_data = {
            'access_code': 'TEST123',
            'email': 'not-an-email'
        }
        form = AccessCodeEmailForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
