import os


from math import radians, cos, sin, asin, sqrt
from django.utils.translation import gettext as _
from django.db import models
from PIL import Image


def profile_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profiles/<filename>
    name, extension = filename.split('.')
    return f'profiles/{instance.id}_{name}.{extension}'


def get_model_field_translations(model):
    """
    Retrieves translated field names for a given model.
    """
    translations = {}
    try:
        model_fields = model.__class__._meta.fields
    except AttributeError:
        model_fields = model._meta.fields

    for field in model_fields:
        if isinstance(field, models.fields.BigAutoField) or isinstance(field, models.fields.related.OneToOneField):
            continue

        if isinstance(field.default, str):
            translations[field.name] = _(field.default)
            # Handle verbose_name if available (skip non-string defaults like booleans)
        elif field.verbose_name and not isinstance(field.default, bool):
            translations[field.name] = _(field.verbose_name)

    return translations


def resize_image(image_path, output_path, size=(300, 300)):
    """
    Resize an image to the specified size.

    :param image_path: Path to the input image.
    :param output_path: Path to save the resized image.
    :param size: Desired size (width, height) tuple. Default is (300, 300).
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail(size, Image.LANCZOS)
            img.save(output_path, "JPEG")

    except Exception as e:
        pass


def delete_file(file_path):
    """
    Deletes the file at the specified path.

    Args:
    file_path (str): The path of the file to delete.

    Returns:
    bool: True if the file was deleted, False otherwise.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        return False




def haversine(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance (km) between two points on Earth."""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    return R * c