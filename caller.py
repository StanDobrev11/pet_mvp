import os
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.pets.models import Pet
from pet_mvp.drugs.models import Vaccine, Drug
from pet_mvp.records.models import VaccinationRecord

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


def populate_drugs():
    treatment_data = [
        dict(
            name='Drontal Puppy',
            notes='Targets roundworms, hookworms and whipworms. Keeping puppy and family away from internal parasites'
        )
    ]

    for data in treatment_data:
        Drug.objects.get_or_create(data)


def populate_vaccines():
    vaccines = [
        dict(
            name='Canine Distemper',
            core=True,
            notes='This core vaccine protects against the highly contagious and potentially deadly distemper virus',
        ),
        dict(
            name='Rabies',
            core=True,
            notes='Rabies is a fatal, viral disease that attacks the central nervous system and usually is transmitted through the bite of an infected animal',
        ),
        dict(
            name='Parvoviridae',
            core=True,
            notes='The vaccine guards against the highly contagious  parvovirus, which causes life-threatening gastrointestinal illness',
        ),
        dict(
            name='Leptospirosis',
            core=True,
            notes='The vaccine protects against leptospirosis, a bacterial infection that can cause kidney and liver failures, bleeding disorder etc.',
        )
    ]

    for data in vaccines:
        Vaccine.objects.get_or_create(data)

    print('Vaccines populated')


def populate_vaccination_records():
    vaccines_data = [
        dict(
            pet=Pet.objects.get(name='Max'),
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='A130D01',
            manufacturer='Nobivac',
            manufacture_date=make_aware(datetime.strptime('18.05.2024', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('22.03.2025', '%d.%m.%Y')),
            valid_until=make_aware(datetime.strptime('22.03.2026', '%d.%m.%Y')),
        )
    ]
    for data in vaccines_data:
        VaccinationRecord.objects.get_or_create(data)

    print('Vaccination records populated')


if __name__ == '__main__':
    create_superuser()
    create_pets()
    populate_vaccines()
    populate_vaccination_records()
