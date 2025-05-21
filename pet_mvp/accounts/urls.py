from django.contrib.auth.decorators import login_not_required
from django.urls import path, include

from pet_mvp.accounts.views import RegisterOwnerView, LoginOwnerView, logout_view, AccessCodeEmailView, \
    PasswordEntryView, ClinicRegistrationView

urlpatterns = [
    path('access-code/', login_not_required(AccessCodeEmailView.as_view()), name='clinic-login'),
    path('password-entry/', login_not_required(PasswordEntryView.as_view()), name='password-entry'),
    path('clinic-register/', login_not_required(ClinicRegistrationView.as_view()), name='clinic-register'),
    path('login/', login_not_required(LoginOwnerView.as_view()), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', login_not_required(RegisterOwnerView.as_view()), name='register'),
]
