import os
import json
import django
from pathlib import Path
from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pet_mvp.settings")
django.setup()

from pet_mvp.drugs.models import Drug, Vaccine
from pet_mvp.accounts.models import Clinic, AppUser, Owner
from pet_mvp.common.models import Testimonial

# Maps model label to actual Django model
MODEL_MAP = {
    "drugs.drug": Drug,
    "drugs.vaccine": Vaccine,
    "accounts.clinic": Clinic,
    "accounts.appuser": AppUser,
    "accounts.owner": Owner,
    "common.testimonial": Testimonial,
}

# Fixture paths
fixture_paths = [
    "pet_mvp/accounts/fixtures/superuser.json",
    "pet_mvp/accounts/fixtures/clinics.json",
    "pet_mvp/drugs/fixtures/cat_vaccines.json",
    "pet_mvp/drugs/fixtures/dog_vaccines.json",
    "pet_mvp/drugs/fixtures/cat_treatments.json",
    "pet_mvp/drugs/fixtures/dog_treatments.json",
    "pet_mvp/common/fixtures/testimonials.json",
]

# Main loader
for path in fixture_paths:
    print(f"📦 Processing fixture: {path}")
    full_path = Path(path)
    if not full_path.exists():
        print(f"❌ File not found: {path}")
        continue

    with open(full_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {path}: {e}")
            continue

    for item in data:
        model_label = item.get("model", "").lower()
        pk = item.get("pk")
        fields = item.get("fields", {})

        model = MODEL_MAP.get(model_label)
        if not model:
            print(f"⚠️ Unknown model: {model_label}")
            continue

        if not pk:
            print(f"⚠️ Missing PK in entry: {item}")
            continue

        # Handle related user reference if applicable
        if model_label in ("accounts.owner", "accounts.clinic") and "user" in fields:
            try:
                user_instance = AppUser.objects.get(pk=fields["user"])
                fields["user"] = user_instance
            except AppUser.DoesNotExist:
                print(f"❌ User with pk={fields['user']} not found for {model_label} #{pk}")
                continue

        obj, created = model.objects.update_or_create(
            pk=pk,
            defaults=fields,
        )

        # Determine best identifier
        identifier = (
            fields.get("name") or
            fields.get("email") or
            fields.get("clinic_name") or
            str(obj)
        )

        action = "🆕 Created" if created else "✅ Updated"
        print(f"{action}: {model.__name__} #{pk} – {identifier}")
