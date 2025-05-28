from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import path, include, reverse_lazy

from pet_mvp.accounts.views import RegisterOwnerView, LoginOwnerView, logout_view, AccessCodeEmailView, \
    PasswordEntryView, ClinicRegistrationView, OwnerDetailsView, OwnerEditView, CustomPasswordResetConfirmView, \
    ApproveTempClinicView

urlpatterns = [
    path('access-code/', login_not_required(AccessCodeEmailView.as_view()),
         name='clinic-login'),
    path('password-entry/', login_not_required(PasswordEntryView.as_view()),
         name='password-entry'),
    path('clinic-register/', login_not_required(ClinicRegistrationView.as_view()),
         name='clinic-register'),
    path('approve-temp-clinic/', login_not_required(ApproveTempClinicView.as_view()), name='approve-temp-clinic'),
    path('login/', login_not_required(LoginOwnerView.as_view()), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', login_not_required(RegisterOwnerView.as_view()), name='register'),
    path('<int:pk>/', include([
        path('details/', OwnerDetailsView.as_view(), name='owner-details'),
        path('edit/', OwnerEditView.as_view(), name='owner-edit')
    ])),
    # Password reset request
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password/password_reset_form.html',
        html_email_template_name='emails/password_reset_email.html',
        success_url='done/',
    ), name='forgot-password'),

    # Reset email sent
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password/password_reset_done.html',
    ), name='password_reset_done'),

    # Password reset link clicked (from email)
    path('reset/<uidb64>/<token>/', login_not_required(CustomPasswordResetConfirmView.as_view(
        template_name='accounts/password/password_reset_confirm.html',
    )), name='password_reset_confirm'),

    # Final confirmation after reset
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password/password_reset_complete.html',
    ), name='password_reset_complete'),

    # Password change views
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password/password_change_form.html',
        success_url=reverse_lazy('password-change-done')
    ), name='password-change'),

    # Password change done view
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password/password_change_done.html'
    ), name='password-change-done'),
]
