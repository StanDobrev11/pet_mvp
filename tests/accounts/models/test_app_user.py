from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()

class AppUserModelTests(TestCase):
    """
    Tests for the AppUser model.
    """
    
    def test_owner_creation(self):
        """Test creating an owner user with valid data."""
        user = UserModel(
            email="owner@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Owner",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        user.save()
        
        self.assertEqual(user.email, "owner@example.com")
        self.assertTrue(user.is_owner)
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "Owner")
        self.assertIsNone(user.clinic_name)
        self.assertIsNone(user.clinic_address)
    
    def test_clinic_creation(self):
        """Test creating a clinic user with valid data."""
        user = UserModel(
            email="clinic@example.com",
            password="testpass123",
            clinic_name="Test Clinic",
            clinic_address="123 Test Street",
            is_owner=False,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        user.save()
        
        self.assertEqual(user.email, "clinic@example.com")
        self.assertFalse(user.is_owner)
        self.assertEqual(user.clinic_name, "Test Clinic")
        self.assertEqual(user.clinic_address, "123 Test Street")
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)
    
    def test_owner_without_name(self):
        """Test that creating an owner without first_name or last_name raises ValidationError."""
        user = UserModel(
            email="owner@example.com",
            password="testpass123",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_owner_with_clinic_info(self):
        """Test that creating an owner with clinic_name or clinic_address raises ValidationError."""
        user = UserModel(
            email="owner@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Owner",
            clinic_name="Test Clinic",  # This should cause validation error
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_clinic_without_clinic_info(self):
        """Test that creating a clinic without clinic_name or clinic_address raises ValidationError."""
        user = UserModel(
            email="clinic@example.com",
            password="testpass123",
            is_owner=False,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_clinic_with_owner_info(self):
        """Test that creating a clinic with first_name or last_name raises ValidationError."""
        user = UserModel(
            email="clinic@example.com",
            password="testpass123",
            clinic_name="Test Clinic",
            clinic_address="123 Test Street",
            first_name="Test",  # This should cause validation error
            is_owner=False,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_str_method_owner(self):
        """Test the __str__ method for Owner proxy model."""
        user = UserModel(
            email="owner@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Owner",
            is_owner=True,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        user.save()
        
        # Get the Owner proxy model instance
        from pet_mvp.accounts.models import Owner
        owner = Owner.objects.get(pk=user.pk)
        
        self.assertEqual(str(owner), "Test Owner owner@example.com")
    
    def test_str_method_clinic(self):
        """Test the __str__ method for Clinic proxy model."""
        user = UserModel(
            email="clinic@example.com",
            password="testpass123",
            clinic_name="Test Clinic",
            clinic_address="123 Test Street",
            is_owner=False,
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        user.save()
        
        # Get the Clinic proxy model instance
        from pet_mvp.accounts.models import Clinic
        clinic = Clinic.objects.get(pk=user.pk)
        
        self.assertEqual(str(clinic), "Test Clinic clinic@example.com")