def pet_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/pets/<filename>
    _, extension = filename.split('.')
    return f'pets/{instance.id}_{instance.name}.{extension}'
