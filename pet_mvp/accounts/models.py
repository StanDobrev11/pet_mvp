from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.managers import UserManager
from pet_mvp.accounts.validators import phone_number_validator
from pet_mvp.common.mixins import TimeStampMixin


# Create your models here.
class AppUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    USERNAME_FIELD = 'email'
    PHONE_NUMBER_LENGTH = 10

    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
        verbose_name=_('Email')
    )

    date_joined = models.DateTimeField(default=timezone.now)

    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text=
        "Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts."
    )

    is_owner = models.BooleanField(
        default=True,
    )

    objects = UserManager()

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_LENGTH,
        validators=[
            phone_number_validator,
        ]
    )

    city = models.CharField(
        max_length=255,
    )

    country = models.CharField(
        max_length=255,
    )

    # Owner-specific fields
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    # Clinic-specific fields
    clinic_name = models.CharField(max_length=255, null=True, blank=True)
    clinic_address = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        """
        Custom validation for field requirements based on is_owner.
        """
        if self.is_owner:
            # Validate that first_name and last_name are provided for owners
            if not self.first_name or not self.last_name:
                raise ValidationError("Owners must have a first name and last name.")
            # Ensure clinic-specific fields remain empty for owners
            if self.clinic_name or self.clinic_address:
                raise ValidationError("Owners cannot have clinic-related information.")
        else:
            # Validate that clinic_name and clinic_address are provided for clinics
            if not self.clinic_name or not self.clinic_address:
                raise ValidationError("Clinics must have a name and address.")
            # Ensure owner-specific fields remain empty for clinics
            if self.first_name or self.last_name:
                raise ValidationError("Clinics cannot have owner-related information.")

        super().clean()

    def save(self, *args, **kwargs):
        # Ensure validation rules are applied before saving
        self.full_clean()  # This calls the `clean` method
        super().save(*args, **kwargs)


class Owner(AppUser):
    class Meta:
        proxy = True
        verbose_name = "Owner"
        verbose_name_plural = "Owners"

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.email}'


class Clinic(AppUser):
    class Meta:
        proxy = True
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"

    def __str__(self):
        return f'{self.clinic_name} {self.email}'
