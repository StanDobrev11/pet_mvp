from django.test import TestCase
from django.db import models
from django.utils import timezone
from datetime import timedelta

from pet_mvp.common.mixins import TimeStampMixin


class TestModel(TimeStampMixin):
    """A test model that uses the TimeStampMixin."""
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'common'  # This is needed for the test model to be recognized


class TimeStampMixinTests(TestCase):
    """
    Tests for the TimeStampMixin.
    """

    def test_fields_existence(self):
        """Test that the mixin adds created_at and updated_at fields."""
        # Get the field names from the model
        field_names = [field.name for field in TestModel._meta.fields]
        
        # Check that the timestamp fields are in the model
        self.assertIn('created_at', field_names)
        self.assertIn('updated_at', field_names)

    def test_created_at_auto_now_add(self):
        """Test that created_at is set to auto_now_add=True."""
        created_at_field = TestModel._meta.get_field('created_at')
        self.assertTrue(created_at_field.auto_now_add)
        self.assertFalse(created_at_field.auto_now)

    def test_updated_at_auto_now(self):
        """Test that updated_at is set to auto_now=True."""
        updated_at_field = TestModel._meta.get_field('updated_at')
        self.assertTrue(updated_at_field.auto_now)
        self.assertFalse(updated_at_field.auto_now_add)

    def test_abstract_model(self):
        """Test that the mixin is an abstract model."""
        self.assertTrue(TimeStampMixin._meta.abstract)