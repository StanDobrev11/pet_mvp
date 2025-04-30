from django.urls import path, include

from pet_mvp.drugs.views import VaccineDetailsView, DrugDetailsView

urlpatterns = [
    path('vaccines/', include([
        path('<int:pk>/', VaccineDetailsView.as_view(), name='vaccine-details')
    ])),
    path('treatments/', include([
        path('<int:pk>/', DrugDetailsView.as_view(), name='treatment-details')
    ]))
]