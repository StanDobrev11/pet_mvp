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


class BaseEditProfileViewTests(TestCase):
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

