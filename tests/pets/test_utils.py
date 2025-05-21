from django.test import TestCase
from unittest.mock import patch, MagicMock
import os

from pet_mvp.pets.utils import pet_directory_path, delete_pet_photo
from pet_mvp.pets.models import Pet
from django.utils import timezone
from datetime import timedelta


class PetUtilsTests(TestCase):
    """
    Tests for the utility functions in the pets module.
    """
    
    def setUp(self):
        """Set up test data."""
        self.today = timezone.now().date()
        self.birth_date = self.today - timedelta(days=365)  # 1 year ago
        
        self.pet = Pet.objects.create(
            name="Buddy",
            species="Dog",
            breed="Labrador",
            sex="male",
            date_of_birth=self.birth_date,
            color="Golden",
            features="Friendly and energetic",
            current_weight=25.5,
            passport_number="AB12345678"
        )
    
    @patch('uuid.uuid4')
    def test_pet_directory_path_new_instance(self, mock_uuid):
        """Test pet_directory_path for a new instance (without pk)."""
        # Mock UUID to return a predictable value
        mock_uuid.return_value = MagicMock(hex='abcdef1234567890')
        
        # Create a new pet instance without saving it (so it has no pk)
        new_pet = Pet(
            name="Max",
            species="Dog",
            breed="German Shepherd",
            sex="male",
            date_of_birth=self.birth_date,
            color="Black and Tan",
            features="Loyal and protective",
            current_weight=30.0,
            passport_number="CD87654321"
        )
        
        # Test with different file extensions
        path = pet_directory_path(new_pet, 'photo.jpg')
        self.assertEqual(path, 'pets/temp/abcdef1234567890.jpg')
        
        path = pet_directory_path(new_pet, 'photo.PNG')
        self.assertEqual(path, 'pets/temp/abcdef1234567890.png')
    
    def test_pet_directory_path_existing_instance(self):
        """Test pet_directory_path for an existing instance (with pk)."""
        # Test with different file extensions
        path = pet_directory_path(self.pet, 'photo.jpg')
        self.assertEqual(path, f'pets/{self.pet.id}_Buddy.jpg')
        
        path = pet_directory_path(self.pet, 'photo.PNG')
        self.assertEqual(path, f'pets/{self.pet.id}_Buddy.png')
    
    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('os.remove')
    def test_delete_pet_photo(self, mock_remove, mock_isfile, mock_listdir):
        """Test delete_pet_photo function."""
        # Mock os.listdir to return a list of files
        mock_listdir.return_value = [
            f'{self.pet.id}_Buddy.jpg',
            'another_file.jpg',
            'some_other_file.png'
        ]
        
        # Mock os.path.isfile to always return True
        mock_isfile.return_value = True
        
        # Call the function
        delete_pet_photo(self.pet)
        
        # Check that os.remove was called with the correct path
        expected_path = os.path.join('pet_mvp', 'media', 'pets', f'{self.pet.id}_Buddy.jpg')
        mock_remove.assert_called_once()
        # Extract the argument and check if it ends with the expected path
        actual_path = mock_remove.call_args[0][0]
        self.assertTrue(actual_path.endswith(f'pets{os.sep}{self.pet.id}_Buddy.jpg'))
    
    @patch('os.listdir')
    @patch('os.remove')
    def test_delete_pet_photo_no_matching_file(self, mock_remove, mock_listdir):
        """Test delete_pet_photo when no matching file is found."""
        # Mock os.listdir to return a list of files that don't match
        mock_listdir.return_value = [
            'another_file.jpg',
            'some_other_file.png'
        ]
        
        # Call the function
        delete_pet_photo(self.pet)
        
        # Check that os.remove was not called
        mock_remove.assert_not_called()
    
    @patch('os.listdir')
    def test_delete_pet_photo_directory_not_found(self, mock_listdir):
        """Test delete_pet_photo when the directory is not found."""
        # Mock os.listdir to raise FileNotFoundError
        mock_listdir.side_effect = FileNotFoundError
        
        # Call the function - it should not raise an exception
        try:
            delete_pet_photo(self.pet)
        except Exception as e:
            self.fail(f"delete_pet_photo raised {type(e).__name__} unexpectedly!")