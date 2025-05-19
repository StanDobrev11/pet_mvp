from django.test import TestCase
from django.db import models
from django.utils.translation import gettext as _
import os
import tempfile
from PIL import Image

from pet_mvp.common.utils import profile_directory_path, get_model_field_translations, resize_image, delete_file


class UtilsTests(TestCase):
    """
    Tests for the utility functions in pet_mvp.common.utils.
    """

    def test_profile_directory_path(self):
        """Test that profile_directory_path returns the correct path."""
        # Create a mock instance with an id
        class MockInstance:
            id = 123

        instance = MockInstance()
        filename = "profile.jpg"

        # Call the function
        path = profile_directory_path(instance, filename)

        # Check the result
        self.assertEqual(path, f"profiles/{instance.id}_profile.jpg")

    def test_get_model_field_translations(self):
        """Test that get_model_field_translations returns the correct translations."""
        # Create a mock model with fields
        class MockField:
            def __init__(self, name, verbose_name=None, default=None):
                self.name = name
                self.verbose_name = verbose_name
                self.default = default

        class MockModel:
            class _meta:
                fields = [
                    MockField("id", None, None),
                    MockField("name", "Name", ""),
                    MockField("is_active", "Is Active", True),
                    MockField("description", "Description", "Default description")
                ]

        model = MockModel()

        # Call the function
        translations = get_model_field_translations(model)

        # Check the result
        self.assertIn("name", translations)
        self.assertIn("description", translations)
        self.assertNotIn("id", translations)  # Should be skipped
        self.assertNotIn("is_active", translations)  # Should be skipped because default is a boolean

    def test_resize_image(self):
        """Test that resize_image resizes an image correctly."""
        # Create a temporary image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Create a simple image
            image = Image.new('RGB', (500, 500), color='red')
            image.save(temp_file.name)

        # Create a temporary output file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as output_file:
            pass

        try:
            # Call the function
            resize_image(temp_file.name, output_file.name, size=(300, 300))

            # Check that the output file exists
            self.assertTrue(os.path.exists(output_file.name))

            # Check that the image was resized
            resized_image = Image.open(output_file.name)
            self.assertLessEqual(resized_image.width, 300)
            self.assertLessEqual(resized_image.height, 300)
            # Close the image to release the file handle
            resized_image.close()
        finally:
            # Clean up
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
            if os.path.exists(output_file.name):
                os.remove(output_file.name)

    def test_delete_file(self):
        """Test that delete_file deletes a file correctly."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")

        try:
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_file.name))

            # Call the function
            result = delete_file(temp_file.name)

            # Check the result
            self.assertTrue(result)

            # Check that the file no longer exists
            self.assertFalse(os.path.exists(temp_file.name))
        finally:
            # Clean up in case the test fails
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    def test_delete_file_nonexistent(self):
        """Test that delete_file returns False for a nonexistent file."""
        # Call the function with a nonexistent file
        result = delete_file("nonexistent_file.txt")

        # Check the result
        self.assertFalse(result)
