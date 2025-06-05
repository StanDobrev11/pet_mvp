import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from pet_mvp.accounts.models import AppUser, Owner, Clinic


class Command(BaseCommand):
    help = 'Dump all AppUsers into a JSON fixture with profiles'

    def handle(self, *args, **kwargs):
        output = []

        for user in AppUser.objects.all():
            if user.is_owner:
                user_data = {
                    "model": "accounts.owner",
                    "fields": {
                        "user": user.pk,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                }

            else:
                user_data = {
                    "model": "accounts.clinic",
                    "fields": {
                        "user": user.pk,
                        "clinic_name": user.clinic_name,
                        "clinic_address": user.clinic_address,
                        "is_approved": user.is_approved,
                    },
                }
            output.append(user_data)

        with open("user_fixtures.json", "w", encoding="utf-8") as f:
            json.dump(output, f, cls=DjangoJSONEncoder, indent=2)

        self.stdout.write(self.style.SUCCESS("User data dumped to user_fixtures.json"))
