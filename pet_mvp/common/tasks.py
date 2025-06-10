from itertools import chain
import requests
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from celery import shared_task

from pet_mvp.accounts.models import Clinic, Groomer, Store

@shared_task
def geocode_venues_coordinates_task():
    api_key = settings.GOOGLE_GEOCODING_API_KEY
    updated_count = 0
    failures = []

    # Efficient lazy evaluation
    all_venues = chain(
        Clinic.objects.select_related("user"),
        Groomer.objects.select_related("user"),
        Store.objects.select_related("user"),
    )

    for venue in all_venues:
        needs_geocoding = (
            venue.latitude is None or
            venue.longitude is None or
            (hasattr(venue.user, "updated_at") and venue.user.updated_at >= now() - timedelta(days=7))
        )

        if not needs_geocoding:
            continue

        address = f"{venue.address}, {venue.user.city}, {venue.user.country}"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            failures.append((venue.id, str(e)))
            continue

        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]
            venue.latitude = location["lat"]
            venue.longitude = location["lng"]
            venue.save()
            updated_count += 1
        else:
            failures.append((venue.id, data.get("status")))

    return {
        "updated": updated_count,
        "failures": failures,
    }
