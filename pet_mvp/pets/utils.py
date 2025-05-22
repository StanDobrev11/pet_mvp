import uuid
import os

from pet_mvp import settings


def pet_directory_path(instance, filename):
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    if instance.pk is None:
        name = f"{uuid.uuid4().hex}{extension}"
        return f'pets/temp/{name}'

    name = f'{instance.id}_{instance.name}{extension}'
    # check if photo exist and delete existing before saving new one
    delete_pet_photo(instance)
    
    return f'pets/{name}'


def delete_pet_photo(instance):
    pets_dir = os.path.join(settings.MEDIA_ROOT, 'pets')
    prefix = f"{instance.id}_{instance.name}"

    try:
        for filename in os.listdir(pets_dir):
            if filename.startswith(prefix):
                file_path = os.path.join(pets_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    break
    except FileNotFoundError:
        pass
