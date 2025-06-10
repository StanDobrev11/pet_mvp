import requests
from datetime import timedelta
from django.utils.timezone import now
from celery import shared_task

from pet_mvp import settings
from pet_mvp.accounts.models import Clinic

@shared_task
def geocode_clinics_task():
    api_key = settings.GOOGLE_MAPS_API_KEY
    updated_count = 0
    failures = []

    clinics = Clinic.objects.all()

    for clinic in clinics:
        needs_geocoding = (
            clinic.latitude is None or
            clinic.longitude is None or
            clinic.user.updated_at >= now() - timedelta(days=7)
        )

        if not needs_geocoding:
            continue

        address = f'{clinic.address}, {clinic.user.city}, {clinic.user.country}'
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            clinic.latitude = location['lat']
            clinic.longitude = location['lng']
            clinic.save()
            updated_count += 1
        else:
            failures.append((clinic.id, data['status']))

    return {
        "updated": updated_count,
        "failures": failures,
    }
