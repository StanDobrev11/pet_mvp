def pet_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/pets/<filename>
    if not instance.id:
        instance.save()

    _, extension = filename.split('.')
    return f'pets/{instance.id}_{instance.name}.{extension}'
