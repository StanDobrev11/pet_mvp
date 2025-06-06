from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.managers import UserManager


class AppUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    PHONE_NUMBER_LENGTH = 32

    LANGUAGE_CHOICES = [
        ('bg', 'BG'),
        ('en', 'EN')
    ]

    email = models.EmailField(
        unique=True,
        error_messages={"unique": _("A user with that email already exists.")},
        verbose_name=_("Email")
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date joined")
    )

    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
        verbose_name=_("Staff status")
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts. "
            "If the user is vet clinic and not active, an email with activation link will be sent "
            "once a valid email address is entered."
        ),
        verbose_name=_("Active")
    )

    is_owner = models.BooleanField(
        default=True,
        verbose_name=_("Owner status")
    )

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_LENGTH,
        blank=True,
        null=True,
        verbose_name=_("Phone number")
    )

    city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("City")
    )

    country = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Country")
    )

    default_language = models.CharField(
        default='bg',
        choices=LANGUAGE_CHOICES,
        verbose_name=_("Default language")
    )

    objects = UserManager()

    def clean(self):
        if self.is_owner and hasattr(self, 'clinic_profile'):
            raise ValidationError(_("An owner cannot have a clinic profile."))
        if not self.is_owner and hasattr(self, 'owner_profile'):
            raise ValidationError(_("A clinic cannot have an owner profile."))
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        if self.is_owner and hasattr(self, 'owner_profile'):
            return f"{self.owner_profile.first_name} {self.owner_profile.last_name}"
        elif not self.is_owner and hasattr(self, 'clinic_profile'):
            return self.clinic_profile.clinic_name
        return self.email

    def __str__(self):
        return self.get_full_name()


class Owner(models.Model):
    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        related_name='owner',
        limit_choices_to={'is_owner': True},
        verbose_name=_("User")
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name=_("First name")
    )

    last_name = models.CharField(
        max_length=255,
        verbose_name=_("Last name")
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Clinic(models.Model):
    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        related_name='clinic',
        limit_choices_to={'is_owner': False},
        verbose_name=_("User")
    )

    clinic_name = models.CharField(
        max_length=255,
        verbose_name=_("Clinic name")
    )

    clinic_address = models.CharField(
        max_length=255,
        verbose_name=_("Clinic address")
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Clinic approved"),
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Latitude")
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Longitude")
    )

    def clean(self):
        if not self.clinic_name or not self.clinic_address:
            raise ValidationError(_("Clinics must have a name and address."))
        super().clean()

    def __str__(self):
        return self.clinic_name
