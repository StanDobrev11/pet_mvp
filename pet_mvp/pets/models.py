from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.common.utils import resize_image
from pet_mvp.pets.utils import pet_directory_path
from pet_mvp.pets.validators import validate_passport_number, validate_transponder_code


UserModel = get_user_model()
class Pet(TimeStampMixin):
    MAX_LENGTH = 50
    PASSPORT_NUMBER_MAX_LENGTH = 12

    SEX_CHOICE = [
        ('male', 'male'),
        ('female', 'female')
    ]

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Name')
    )

    species = models.CharField(
        max_length=MAX_LENGTH,
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
            "unique": "A pet with this details already exists.",
        },
    )

    owners = models.ManyToManyField(
        to=UserModel,
        related_name='pets'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            resize_image(self.photo.path, self.photo.path)

    @property
    def age(self):
        years = (timezone.now().date() - self.date_of_birth).days // 365
        months = (timezone.now().date() - self.date_of_birth).days % 365 // 30
        days = (timezone.now().date() - self.date_of_birth).days % 365 % 30

        return _('{} years, {} months and {} days').format(years, months, days)

    def __str__(self):
        return f'{self.name} - {self.species} - {self.breed}'



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
