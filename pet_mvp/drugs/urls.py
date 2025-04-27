from django.urls import path, include

from pet_mvp.drugs.views import VaccineDetailsView

urlpatterns = [
    path('vaccines/', include([
        path('<int:pk>/', VaccineDetailsView.as_view(), name='vaccine-details')
    ]))
]