from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.managers import UserManager
from pet_mvp.accounts.validators import phone_number_validator
from pet_mvp.common.mixins import TimeStampMixin

# Create your models here.
class AppUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    USERNAME_FIELD = 'email'

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

    objects = UserManager()

    def __str__(self):
        return self.email


class Owner(models.Model):
    PHONE_NUMBER_LENGTH = 10

    first_name = models.CharField(
        max_length=255,
    )

    last_name = models.CharField(
        max_length=255,
    )

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_LENGTH,
        validators=[
            phone_number_validator,
        ]
    )

    city = models.CharField(
        max_length=255,
    )

    user = models.OneToOneField(
        to=AppUser,
        on_delete=models.CASCADE,
        related_name='owner',
    )