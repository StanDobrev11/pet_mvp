import os
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

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

if __name__ == '__main__':
    create_superuser()