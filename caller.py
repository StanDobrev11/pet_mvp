import os
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


def create_superuser(email='admin@pet_mvp.com', password='1234'):
    try:
        UserModel.objects.create_superuser(
            email=email,
            password=password,
        )
        print('Superuser created')
    except IntegrityError:
        print('Superuser already exists')

    print(f'email: {email}\npassword: {password}')


def create_user(email, password):
    try:
        UserModel.objects.create_user(
            email=email,
            password=password,
        )
        print('User created')
    except IntegrityError:
        print('User already exists')

    print(f'email: {email}\npassword: {password}')


def create_pets():
    try:
        max_pet = Pet.objects.create(
            name='Max',
            species='Dog',
            breed='German Shepherd',
            color='Black and Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )
        luna_pet = Pet.objects.create(
            name='Luna',
            species='Cat',
            breed='Persian',
            color='White',
            date_of_birth='2021-03-15',
            sex='female',
            current_weight='3.5',
            passport_number='BG01ST765214',
        )
        pets = [max_pet, luna_pet]

        owner = UserModel.objects.first()

        for pet in pets:
            pet.owners.add(owner)
        print('Pets created')
    except IntegrityError:
        print('Pets already exist')



if __name__ == '__main__':
    create_superuser()
    create_pets()
