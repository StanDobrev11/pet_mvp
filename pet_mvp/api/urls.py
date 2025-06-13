from django.urls import path

from pet_mvp.api.views import verify_access_code, get_pet_events, get_venues_nearby, health_check

urlpatterns = [
    path('access-code/', verify_access_code, name='verify-access-code'),
    path('calendar/', get_pet_events, name='get-pet-events'),
    path('venues/nearby/', get_venues_nearby, name='venues-nearby'),
    path('health/', health_check, name='health-check'),
]