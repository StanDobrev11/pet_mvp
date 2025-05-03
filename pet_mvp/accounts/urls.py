from django.urls import path, include

from pet_mvp.accounts.views import RegisterOwnerView, LoginOwnerView, logout_view, AccessCodeEmailView, \
    PasswordEntryView, ClinicRegistrationView

urlpatterns = [
    path('access-code/', AccessCodeEmailView.as_view(), name='clinic-login'),
    path('password-entry/', PasswordEntryView.as_view(), name='password-entry'),
    path('clinic-register/', ClinicRegistrationView.as_view(), name='clinic-register'),
    path('login/', LoginOwnerView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterOwnerView.as_view(), name='register'),
]
