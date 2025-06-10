from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.utils import haversine
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import VetPetAccess
from pet_mvp.records.models import VaccinationRecord, MedicationRecord
from django.utils import timezone
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from pet_mvp.accounts.models import Clinic, Store, Groomer


# Create your views here.
@require_POST
@login_required
def verify_access_code(request):
    code = request.POST.get('access_code')
    try:
        pet = Pet.objects.get(pet_access_code__code=code)
    except Pet.DoesNotExist:
        return JsonResponse({'error': 'Invalid access code'}, status=400)

    # Grant temporary access
    VetPetAccess.objects.update_or_create(
        vet=request.user,
        pet=pet,
        defaults={
            'created_at': timezone.now(),
            'expires_at': timezone.now() + timedelta(minutes=10),
            'granted_by': 'code'
        }
    )

    return JsonResponse({
        'pet_name': pet.name,
        'pet_id': pet.id,
        'species': pet.species,
        'age': pet.age,
        'photo_url': pet.photo.url if pet.photo else '',

        'owners': [
            {
                'pk': owner.pk,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'full_name': owner.get_full_name()
            }
            for owner in pet.owners.all()
        ]
    })

@login_required
def get_pet_events(request):
    if not request.user.is_owner:
        return JsonResponse({'error': 'Not authorized'}, status=401)

    today = timezone.now()
    two_years_ago = today - timedelta(days=730)

    pets = request.user.pets.all()

    # Prefetch vaccination and medication records, filtered
    pets = pets.prefetch_related(
        Prefetch(
            'vaccine_records',
            queryset=VaccinationRecord.objects.filter(valid_until__gte=two_years_ago).select_related('vaccine')
        ),
        Prefetch(
            'medication_records',
            queryset=MedicationRecord.objects.filter(
                date__gte=two_years_ago
            ).select_related('medication')
        )
    )

    events = []
    for pet in pets:
        # Vaccination Records
        for v in pet.vaccine_records.all():
            due_date = v.valid_until
            days_remaining = (due_date - today.date()).days

            if days_remaining <= 7:
                # Vaccination due soon
                events.append({
                    "title": f"💉 {pet.name} – {v.vaccine.name} ({_('Due Soon')})",
                    "start": v.valid_until.isoformat(),
                    "color": "#ffc107",  # orange/yellow
                    "textColor": "#000",
                    "borderColor": "#ffcd39",
                    "allDay": True,
                    "classNames": ["urgent-vaccine"],
                })
            else:
                # Not urgent
                events.append({
                    "title": f"💉 {pet.name} – {v.vaccine.name} ({_('Due Date')})",
                    "start": v.valid_until.isoformat(),
                    "color": "#e2e3e5",  # muted gray
                    "textColor": "#6c757d",  # muted text
                    "borderColor": "#ced4da",
                    "allDay": True,
                    "classNames": ["dimmed-vaccine"],
                })

        # Medication Records
        for m in pet.medication_records.all():
            due_date = m.valid_until
            days_remaining = (due_date - today.date()).days

            if days_remaining <= 7:
                events.append({
                    "title": f"💊 {pet.name} – {m.medication.name} ({_('Due Soon')})",
                    "start": m.valid_until.isoformat(),
                    "color": "#dc3545",  # red
                    "textColor": "#fff",
                    "borderColor": "#b02a37",
                    "allDay": True,
                    "classNames": ["urgent-medication"],
                   })
            else:
                events.append({
                    "title": f"💊 {pet.name} – {m.medication.name} ({_('Due Date')})",
                    "start": m.valid_until.isoformat(),
                    "color": "#dee2e6",  # light gray-blue
                    "textColor": "#495057",
                    "borderColor": "#adb5bd",
                    "allDay": True,
                    "classNames": ["dimmed-medication"],
                  })

    return JsonResponse(events, safe=False)


@require_GET
def get_venues_nearby(request):
    try:
        user_lat = float(request.GET.get("lat"))
        user_lng = float(request.GET.get("lng"))
        radius = float(request.GET.get("radius", 5))
        venue_type= request.GET.get("type")

    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid or missing parameters."}, status=400)

    nearby_venues = []

    venue_class_mapper = {
        'clinic': Clinic,
        'store': Store,
        'groomer': Groomer
    }

    for venue in venue_class_mapper[venue_type].objects.filter(is_approved=True, latitude__isnull=False, longitude__isnull=False):
        dist = haversine(user_lat, user_lng, venue.latitude, venue.longitude)
        if dist <= radius:
            nearby_venues.append({
                "id": venue.id,
                "name": venue.name,
                "address": venue.address,
                "lat": venue.latitude,
                "lng": venue.longitude,
                "distance_km": round(dist, 2),
                "website": venue.website,
            })

    return JsonResponse({"results": nearby_venues})