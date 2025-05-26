import os
import json
import django
from pathlib import Path
from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pet_mvp.settings")
django.setup()

from pet_mvp.drugs.models import Drug, Vaccine
from pet_mvp.accounts.models import Clinic

# Maps model label to actual Django model
MODEL_MAP = {
    "drugs.drug": Drug,
    "drugs.vaccine": Vaccine,
    "accounts.clinic": Clinic,
}

# Paths to your fixtures
fixture_paths = [
    "pet_mvp/accounts/fixtures/clinics.json",
    "pet_mvp/drugs/fixtures/cat_vaccines.json",
    "pet_mvp/drugs/fixtures/dog_vaccines.json",
    "pet_mvp/drugs/fixtures/cat_treatments.json",
    "pet_mvp/drugs/fixtures/dog_treatments.json",
]

# Main loader
for path in fixture_paths:
    print(f"Processing fixture: {path}")
    full_path = Path(path)
    if not full_path.exists():
        print(f"❌ File not found: {path}")
        continue

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        model_label = item["model"]
        pk = item["pk"]
        fields = item["fields"]

        model = MODEL_MAP.get(model_label)
        if not model:
            print(f"⚠️ Unknown model: {model_label}")
            continue

        # Update or create by PK
        obj, created = model.objects.update_or_create(
            pk=pk,
            defaults=fields,
        )
        action = "🆕 Created" if created else "✅ Updated"
        print(f"{action}: {model.__name__} #{pk} – {fields.get('name')}")
