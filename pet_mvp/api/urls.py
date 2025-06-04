from django.urls import path

from pet_mvp.api.views import verify_access_code, get_pet_events

urlpatterns = [
    path('access-code/', verify_access_code, name='verify-access-code'),
    path('calendar/', get_pet_events, name='get-pet-events'),
]