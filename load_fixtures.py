# load_fixtures.py

import os
import django
from django.core.management import call_command

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pet_mvp.settings")
django.setup()

# Paths to your fixtures
fixture_paths = [
    "pet_mvp/accounts/fixtures/clinics.json",
    "pet_mvp/drugs/fixtures/cat_vaccines.json",
    "pet_mvp/drugs/fixtures/dog_vaccines.json",
    "pet_mvp/drugs/fixtures/cat_treatments.json",
    "pet_mvp/drugs/fixtures/dog_treatments.json",

]

# Load each fixture
for path in fixture_paths:
    print(f"Loading fixture: {path}")
    call_command('loaddata', path)
