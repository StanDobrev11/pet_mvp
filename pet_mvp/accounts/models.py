from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.managers import UserManager
from pet_mvp.accounts.validators import normalize_bulgarian_phone, phone_number_validator
from pet_mvp.common.mixins import TimeStampMixin


# Create your models here.
class AppUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    USERNAME_FIELD = 'email'
    PHONE_NUMBER_LENGTH = 14
    
    LANGUAGE_CHOICES = [
        ('bg', 'BG'),
        ('en', 'EN')
    ]

    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
        verbose_name=_('Email')
    )

    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date joined"))

    is_staff = models.BooleanField(
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
        verbose_name=_("Staff status"),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts. "
            "If the user is vet clinic and not active, an email with activation link will be sent "
            "one valid email address is entered"
        ),
        verbose_name=_("Active"),
    )

    is_owner = models.BooleanField(
        default=True,
        verbose_name=_("Owner status"),
    )

    objects = UserManager()

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_LENGTH,
        verbose_name=_("Phone number"),
    )

    city = models.CharField(
        max_length=255,
        verbose_name=_("City"),
    )

    country = models.CharField(
        max_length=255,
        verbose_name=_("Country"),
    )
    
    default_language = models.CharField(
        default='bg',
        choices=LANGUAGE_CHOICES
    )
    
    # Owner-specific fields
    first_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("First name"))
    last_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Last name"))

    # Clinic-specific fields
    clinic_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Clinic name"))
    clinic_address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Clinic address"))
    is_approved = models.BooleanField(
        verbose_name=_("Clinic approved"),
        null=True,
        blank=True
    )


    def clean(self):
        """
        Custom validation for field requirements based on is_owner.
        """        
        if self.is_owner:
            # Validate that first_name and last_name are provided for owners
            if not self.first_name or not self.last_name:
                raise ValidationError(
                    _("Owners must have a first name and last name."))
            # Ensure clinic-specific fields remain empty for owners
            if self.clinic_name or self.clinic_address:
                raise ValidationError(
                    _("Owners cannot have clinic-related information."))
        else:
            # Validate that clinic_name and clinic_address are provided for clinics
            if not self.clinic_name or not self.clinic_address:
                raise ValidationError(
                    _("Clinics must have a name and address."))
            # Ensure owner-specific fields remain empty for clinics
            if self.first_name or self.last_name:
                raise ValidationError(
                    _("Clinics cannot have owner-related information."))
            # Ensure is_approved is set to False for clinic creation
            if self.is_approved is None:
                self.is_approved = False

        super().clean()

    def save(self, *args, **kwargs):
        # Ensure validation rules are applied before saving
        self.full_clean()  # This calls the `clean` method
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class Owner(AppUser):
    class Meta:
        proxy = True
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.email}'


class Clinic(AppUser):
    class Meta:
        proxy = True
        verbose_name = _("Clinic")
        verbose_name_plural = _("Clinics")

    def __str__(self):
        return f'{self.clinic_name} {self.email}'
