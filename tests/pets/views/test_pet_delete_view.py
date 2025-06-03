from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class PetViewsTest(TestCase):
    def setUp(self):
        self.pet = Pet.objects.create(
            name_en='New Pet',
            species='dog',
            breed='Retriever',
            color='Golden',
            date_of_birth='2020-05-01',
            sex='male',
            current_weight='30',
            passport_number='BG01VP123456',
        )

        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.second_owner = UserModel.objects.create_owner(
            email='second_owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.pet.owners.add(self.owner)
        self.client_owner = Client()
        self.client_owner.login(email='owner@example.com', password='testpass123')

    def test_pet_deleted(self):

        self.assertTrue(Pet.objects.filter(pk=self.pet.pk).exists())

        url = reverse('pet-delete', kwargs={'pk': self.pet.pk})

        response = self.client_owner.post(url)
        self.assertFalse(Pet.objects.filter(pk=self.pet.pk).exists())
        self.assertRedirects(response, reverse('dashboard'))

    def test_pet_delete_removed_from_current_user(self):

        self.pet.owners.add(self.second_owner)
        self.assertIn(self.owner, self.pet.owners.all())
        self.assertIn(self.second_owner, self.pet.owners.all())

        url = reverse('pet-delete', kwargs={'pk': self.pet.pk})
        response = self.client_owner.post(url)

        # ensure pet exists
        self.assertTrue(Pet.objects.filter(pk=self.pet.pk).exists())
        # ensure first owner is out
        self.assertNotIn(self.owner, self.pet.owners.all())
        # ensure second owner remain
        self.assertIn(self.second_owner, self.pet.owners.all())
        # ensure redirect
        self.assertRedirects(response, reverse('dashboard'))