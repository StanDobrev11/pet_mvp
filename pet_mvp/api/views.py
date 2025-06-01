from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from pet_mvp.pets.models import Pet
from pet_mvp.access_codes.models import VetPetAccess
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