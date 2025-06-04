from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from pet_mvp.drugs.models import Vaccine, Drug
from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import VetPetAccess
from pet_mvp.records.models import VaccinationRecord, MedicationRecord


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

from django.utils import timezone
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import timedelta

@login_required
def get_pet_events(request):
    if not request.user.is_owner:
        return JsonResponse({'error': 'Not authorized'}, status=401)

    today = timezone.now()
    one_month_ago = today - timedelta(days=30)

    pets = request.user.pets.all()

    # Prefetch vaccination and medication records, filtered
    pets = pets.prefetch_related(
        Prefetch(
            'vaccine_records',
            queryset=VaccinationRecord.objects.filter(valid_until__gte=one_month_ago).select_related('vaccine')
        ),
        Prefetch(
            'medication_records',
            queryset=MedicationRecord.objects.filter(
                created_at__gte=one_month_ago
            ).select_related('medication')
        )
    )

    events = []

    for pet in pets:
        for v in pet.vaccine_records.all():
            events.append({
                "title": f"💉 {pet.name} – {v.vaccine.name}",
                "start": v.valid_until.isoformat(),
                "color": "#28a745",
            })

        for m in pet.medication_records.all():
            events.append({
                "title": f"💊 {pet.name} – {m.medication.name}",
                "start": m.created_at.date().isoformat(),
                "end": m.valid_until.isoformat() if m.valid_until else None,
                "color": "#17a2b8",
            })

    return JsonResponse(events, safe=False)
