from django.urls import path, include
from django.contrib.auth.decorators import login_not_required

from pet_mvp.pets.views import ApprovePetAdditionView, PetDetailView, PetEditView, PetAddView, PetDeleteView, MarkingAddView, MarkingDetailsView, AddExistingPetView

urlpatterns = [
    path('add/', PetAddView.as_view(), name='pet-add'),
    path('add-existing/', AddExistingPetView.as_view(), name='pet-add-existing'),
    path('pets/approve/<str:token>/', login_not_required(ApprovePetAdditionView.as_view()),
         name='approve-pet-addition'),
    path('<int:pk>/',
         include([
             path('details/', PetDetailView.as_view(), name='pet-details'),
             path('edit/', PetEditView.as_view(), name='pet-edit'),
             path('delete/', PetDeleteView.as_view(), name='pet-delete'),
             path('marking/',
                  include([
                      path('add/', MarkingAddView.as_view(), name='marking-add'),
                      path('details/', MarkingDetailsView.as_view(),
                           name='marking-details')
                  ])),
         ])
         )
]
