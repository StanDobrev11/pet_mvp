from django.urls import path, include

from pet_mvp.pets.views import PetDetailView, PetEditView, PetAddView, PetDeleteView, MarkingAddView, MarkingDetailsView

urlpatterns = [
    path('add/', PetAddView.as_view(), name='pet-add'),
    path('<int:pk>/',
         include([
             path('details/', PetDetailView.as_view(), name='pet-details'),
             path('edit/', PetEditView.as_view(), name='pet-edit'),
             path('delete/', PetDeleteView.as_view(), name='pet-delete'),
             path('marking/',
                  include([
                      path('add/', MarkingAddView.as_view(), name='marking-add'),
                      path('details/', MarkingDetailsView.as_view(), name='marking-details')
                  ])),
         ])
         )
]
