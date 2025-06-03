from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import activate

from pet_mvp.pets.models import Pet

UserModel = get_user_model()

class PetViewsTest(TestCase):
    def setUp(self):
        activate('en')

        self.owner = UserModel.objects.create_owner(
            email='owner@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Owner',
            phone_number='0887654321',
            city='Sofia',
            country='Bulgaria'
        )

        self.client_owner = Client()
        self.client_owner.login(email='owner@example.com', password='testpass123')
        self.client_owner.cookies.load({'django_language': 'en'})

    def test_pet_add_view(self):
        url = reverse('pet-add')

        data = dict(
            name_en='Test Pet',
            name_bg='Тестово Животно',
            species='dog',
            breed='German Shepherd',
            color='Black and Tan',
            color_en='Black and Tan',
            color_bg='Черно и кафяво',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
            features='Friendly, energetic, loyal',
            features_en='Friendly, energetic, loyal',
            features_bg='Приятелски настроен, енергичен, лоялен',
        )
        response = self.client_owner.post(url, data)

        self.assertRedirects(response, reverse('dashboard'))
        new_pet = Pet.objects.get(name_en='Test Pet')
        self.assertIn(self.owner, new_pet.owners.all())

    def test_pet_add_view_missing_passport_number(self):
        url = reverse('pet-add')

        data = dict(
            name_en='Missing Passport Pet',
            species='dog',
            breed='Retriever',
            color='Golden',
            date_of_birth='2020-05-01',
            sex='male',
            current_weight='30',
            # passport_number omitted
        )
        response = self.client_owner.post(url, data)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('passport_number', form.errors)
        self.assertIn('This field is required.', form.errors['passport_number'])


    def test_pet_add_view_invalid_passport_number(self):
        url = reverse('pet-add')

        data = dict(
            name_en='Invalid Passport Pet',
            species='dog',
            breed='Retriever',
            color='Golden',
            date_of_birth='2020-05-01',
            sex='male',
            current_weight='30',
            passport_number='INVALID$$$',  # assuming you validate format
        )
        response = self.client_owner.post(url, data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)

        self.assertIn('passport_number', form.errors)
        self.assertIn('INVALID$$$ is not a valid passport number. The format must be BG01VP123456.', form.errors['passport_number'])
