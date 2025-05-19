import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.settings import MEDIA_ROOT
from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.common.utils import resize_image
from pet_mvp.pets.utils import pet_directory_path, delete_pet_photo
from pet_mvp.pets.validators import validate_passport_number, validate_transponder_code

UserModel = get_user_model()


class Pet(TimeStampMixin):
    MAX_LENGTH = 50
    PASSPORT_NUMBER_MAX_LENGTH = 12

    SEX_CHOICE = [
        ('male', _('Male')),
        ('female', _('Female'))
    ]

    SPECIES_CHOICE = [
        ('dog', _('Dog')),
        ('cat', _('Cat')),
    ]

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Name')
    )

    species = models.CharField(
        max_length=MAX_LENGTH,
        choices=SPECIES_CHOICE,
        verbose_name=_('Species')
    )

    breed = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Breed')
    )

    sex = models.CharField(
        max_length=6,
        choices=SEX_CHOICE,
        verbose_name=_('Sex')
    )

    date_of_birth = models.DateField(
        verbose_name=_('Date of birth')
    )

    color = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Color')
    )

    features = models.CharField(
        max_length=255,
        verbose_name=_('Any notable or discernible features or characteristics')
    )

    photo = models.ImageField(
        upload_to=pet_directory_path,
        blank=True,
        null=True,
        verbose_name=_('Photo')
    )

    current_weight = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name=_('Current weight')
    )

    passport_number = models.CharField(
        max_length=PASSPORT_NUMBER_MAX_LENGTH,
        validators=[validate_passport_number],
        verbose_name=_('Passport Number'),
        unique=True,
        error_messages={
            "unique": _("A pet with this details already exists."),
        },
    )

    can_add_vaccines = models.BooleanField(
        default=True,
        verbose_name=_('Can add vaccines?'),
        help_text=_('Controls if the owner can add vaccines.'),
    )

    can_add_treatments = models.BooleanField(
        default=True,
        verbose_name=_('Can add treatments?'),
        help_text=_('Controls if the owner can add treatments.'),
    )

    owners = models.ManyToManyField(
        to=UserModel,
        related_name='pets'
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super(Pet, self).save(*args, **kwargs)

        # Rename only for newly created objects and only if a photo was uploaded
        if is_new and self.photo:
            _, extension = os.path.splitext(self.photo.name)
            new_name = f'pets/{self.id}_{self.name}{extension}'

            new_path = os.path.join(MEDIA_ROOT, new_name)
            current_path = self.photo.path

            # Only rename if file path is different
            if current_path != new_path:
                # Move file
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                os.rename(current_path, new_path)

                # Update model field with new path
                self.photo.name = new_name
                # Save again to update file path in DB without triggering recursion
                super(Pet, self).save(update_fields=['photo'])

        # Resize after saving
        if self.photo:
            from django.db import transaction
            transaction.on_commit(lambda: resize_image(self.photo.path, self.photo.path))
        else:
            delete_pet_photo(self)

    @property
    def age(self):
        years = (timezone.now().date() - self.date_of_birth).days // 365
        months = (timezone.now().date() - self.date_of_birth).days % 365 // 30
        days = (timezone.now().date() - self.date_of_birth).days % 365 % 30

        return _('{} years, {} months and {} days').format(years, months, days)

    def __str__(self):
        return f'{self.name} - {self.get_species_display()} - {self.breed} - {self.get_sex_display()}'


class BaseMarking(models.Model):
    CODE_MAX_LENGTH = 50
    LOCATION_MAX_LENGTH = 255

    class Meta:
        abstract = True

    type = models.CharField(
        max_length=11,
        verbose_name=_('Type')
    )

    code = models.CharField(
        max_length=CODE_MAX_LENGTH
    )

    pet = models.OneToOneField(
        to=Pet,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.__class__.__name__} - {self.code}'

    def save(self, *args, **kwargs):
        self.type = self.__class__.__name__
        super().save(*args, **kwargs)


class Transponder(BaseMarking):
    CODE_MAX_LENGTH = 15

    code = models.CharField(
        unique=True,
        primary_key=True,
        max_length=BaseMarking.CODE_MAX_LENGTH,
        validators=[validate_transponder_code],
        verbose_name=_('Transponder alphanumeric code')
    )

    date_of_application = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of application or reading of the transponder')
    )

    date_of_reading = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of application or reading of the transponder')
    )

    location = models.CharField(
        max_length=BaseMarking.LOCATION_MAX_LENGTH,
        verbose_name=_('Location of the transponder')
    )


class Tattoo(BaseMarking):
    code = models.CharField(
        unique=True,
        primary_key=True,
        max_length=BaseMarking.CODE_MAX_LENGTH,
        verbose_name=_('Tattoo alphanumeric code')
    )

    date_of_application = models.DateField(
        verbose_name=_('Date of application of the tattoo')
    )

    date_of_reading = models.DateField(
        verbose_name=_('Date of reading of the tattoo')
    )

    location = models.CharField(
        max_length=BaseMarking.LOCATION_MAX_LENGTH,
        verbose_name=_('Location of the tattoo')
    )
