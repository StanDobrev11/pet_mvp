from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from pet_mvp.accounts.models import Owner, Clinic

UserModel = get_user_model()

class AppUserModelTests(TestCase):
    """
    Tests for the AppUser model.
    """
    
    def test_owner_creation(self):
        """Test creating an owner user and related profile."""
        user = UserModel.objects.create(
            email="owner@example.com",
            password="testpass123",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        owner = Owner.objects.create(user=user, first_name="Test", last_name="Owner")

        self.assertEqual(user.email, "owner@example.com")
        self.assertTrue(user.is_owner)
        self.assertEqual(owner.first_name, "Test")
        self.assertEqual(owner.last_name, "Owner")
    
    def test_clinic_creation(self):
        """Test creating a clinic user and related profile."""
        user = UserModel.objects.create(
            email="clinic@example.com",
            password="testpass123",
            is_owner=False,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        clinic = Clinic.objects.create(user=user, clinic_name="Test Clinic", clinic_address="123 Test Street")

        self.assertEqual(user.email, "clinic@example.com")
        self.assertFalse(user.is_owner)
        self.assertEqual(clinic.clinic_name, "Test Clinic")
        self.assertEqual(clinic.clinic_address, "123 Test Street")

    def test_missing_owner_profile_fields(self):
        """Owner profile must have first_name and last_name."""
        user = UserModel.objects.create(
            email="owner2@example.com",
            password="testpass123",
            is_owner=True,
        )
        owner = Owner(user=user)

        with self.assertRaises(ValidationError):
            owner.full_clean()

    def test_missing_clinic_profile_fields(self):
        """Clinic profile must have clinic_name and clinic_address."""
        user = UserModel.objects.create(
            email="clinic2@example.com",
            password="testpass123",
            is_owner=False,
        )
        clinic = Clinic(user=user)

        with self.assertRaises(ValidationError):
            clinic.full_clean()

    def test_str_method_owner(self):
        """Test Owner.__str__ method."""
        user = UserModel.objects.create(
            email="owner3@example.com",
            password="testpass123",
            is_owner=True
        )
        owner = Owner.objects.create(user=user, first_name="Test", last_name="Owner")
        self.assertEqual(str(owner), "Test Owner")

    def test_str_method_clinic(self):
        """Test Clinic.__str__ method."""
        user = UserModel.objects.create(
            email="clinic3@example.com",
            password="testpass123",
            is_owner=False
        )
        clinic = Clinic.objects.create(user=user, clinic_name="Vet Clinic", clinic_address="Some St.")
        self.assertEqual(str(clinic), "Vet Clinic")