from django.urls import path, include

from pet_mvp.accounts.views import RegisterUserView, LoginUserView, logout_view
from pet_mvp.common.views import DashboardView

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterUserView.as_view(), name='register'),
]
