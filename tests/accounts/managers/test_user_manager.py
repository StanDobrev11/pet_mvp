from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()

class UserManagerTests(TestCase):
    """
    Tests for the UserManager class that handles user creation.
    """

    def test_create_user_with_empty_email(self):
        """Test that creating a user with an empty email raises ValueError."""
        with self.assertRaises(ValueError):
            UserModel.objects.create_owner(
                email="", 
                password="testpass123",
                first_name="Test",
                last_name="User",
                phone_number="0887654321",
                city="Sofia",
                country="Bulgaria"
            )

    def test_create_user_with_empty_password(self):
        """Test that creating a user with an empty password raises ValueError."""
        with self.assertRaises(ValueError):
            UserModel.objects.create_owner(
                email="test@example.com", 
                password="",
                first_name="Test",
                last_name="User",
                phone_number="0887654321",
                city="Sofia",
                country="Bulgaria"
            )

    def test_create_owner(self):
        """Test creating an owner user."""
        user = UserModel.objects.create_owner(
            email="owner@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Owner",
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

        self.assertEqual(user.email, "owner@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_owner)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.owner.first_name, "Test")
        self.assertEqual(user.owner.last_name, "Owner")
        self.assertEqual(user.phone_number, "0887654321")
        self.assertEqual(user.city, "Sofia")
        self.assertEqual(user.country, "Bulgaria")

    def test_create_clinic(self):
        """Test creating a clinic user."""
        user = UserModel.objects.create_clinic(
            email="clinic@example.com",
            password="testpass123",
            name="Test Clinic",
            address="123 Test Street",
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

        self.assertEqual(user.email, "clinic@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_owner)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.clinic.name, "Test Clinic")
        self.assertEqual(user.clinic.address, "123 Test Street")
        self.assertEqual(user.phone_number, "0887654321")
        self.assertEqual(user.city, "Sofia")
        self.assertEqual(user.country, "Bulgaria")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = UserModel.objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )

        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_owner)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_with_is_staff_false(self):
        """Test that creating a superuser with is_staff=False raises ValueError."""
        with self.assertRaises(ValueError):
            UserModel.objects.create_superuser(
                email="admin@example.com",
                password="testpass123",
                first_name="Admin",
                last_name="User",
                phone_number="0887654321",
                city="Sofia",
                country="Bulgaria",
                is_staff=False
            )

    def test_create_superuser_with_is_superuser_false(self):
        """Test that creating a superuser with is_superuser=False raises ValueError."""
        with self.assertRaises(ValueError):
            UserModel.objects.create_superuser(
                email="admin@example.com",
                password="testpass123",
                first_name="Admin",
                last_name="User",
                phone_number="0887654321",
                city="Sofia",
                country="Bulgaria",
                is_superuser=False
            )

    def test_email_normalization(self):
        """Test that email addresses are normalized when creating a user."""
        email = "test@EXAMPLE.COM"
        user = UserModel.objects.create_owner(
            email=email, 
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="0887654321",
            city="Sofia",
            country="Bulgaria"
        )
        self.assertEqual(user.email, email.lower())
