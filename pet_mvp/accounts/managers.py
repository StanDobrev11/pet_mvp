from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import transaction

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save an AppUser with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        if not password:
            raise ValueError("The given password must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    @transaction.atomic
    def create_owner(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        from pet_mvp.accounts.models import Owner  # Avoid circular import

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_owner", True)

        user = self._create_user(email, password, **extra_fields)

        if not first_name or not last_name:
            raise ValueError("Owner must have first_name and last_name.")

        Owner.objects.create(user=user, first_name=first_name, last_name=last_name)
        return user

    @transaction.atomic
    def create_clinic(self, email, password=None, name=None, address=None, is_approved=False, **extra_fields):
        from pet_mvp.accounts.models import Clinic  # Avoid circular import

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_owner", False)
        extra_fields.setdefault("is_clinic", True)

        user = self._create_user(email, password, **extra_fields)

        if not name or not address:
            raise ValueError("Clinic must have clinic_name and clinic_address.")

        Clinic.objects.create(user=user, name=name, address=address, is_approved=is_approved)
        return user

    def create_superuser(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        from pet_mvp.accounts.models import Owner  # Avoid circular import

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_owner", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self._create_user(email, password, **extra_fields)

        Owner.objects.create(user=user, first_name=first_name, last_name=last_name)

        return user
