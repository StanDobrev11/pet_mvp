from django.urls import path

from pet_mvp.api.views import verify_access_code

urlpatterns = [
    path('access-code/', verify_access_code, name='verify-access-code'),
]