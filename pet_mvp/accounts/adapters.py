from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from pet_mvp.accounts.models import Owner

UserModel = get_user_model()

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.internal.userkit import user_email, user_username
from allauth.account.utils import valid_email_or_none
from pet_mvp.accounts.models import Owner
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Populate base user fields only (email, username).
        First and last name are handled in save_user via Owner profile.
        """
        email = data.get("email")

        user = sociallogin.user
        user_email(user, valid_email_or_none(email) or "")
        user.is_owner = True  # Default to owner for social login

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user and create/update the Owner profile with name fields.
        """
        user = super().save_user(request, sociallogin, form)

        extra_data = sociallogin.account.extra_data
        first_name = extra_data.get("given_name") or extra_data.get("name", "").split(" ")[0]
        last_name = extra_data.get("family_name") or extra_data.get("name", "").split(" ")[-1]

        if user.is_owner:
            owner, _ = Owner.objects.get_or_create(user=user)
            if first_name:
                owner.first_name = first_name
            if last_name:
                owner.last_name = last_name
            owner.save()

        return user
