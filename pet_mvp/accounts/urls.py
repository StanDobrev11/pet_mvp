from django.urls import path, include

from pet_mvp.accounts.views import RegisterUserView, LoginUserView

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('register/', RegisterUserView.as_view(), name='register'),
]
