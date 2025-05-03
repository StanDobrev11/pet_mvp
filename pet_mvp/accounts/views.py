from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic as views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from pet_mvp.accounts.forms import OwnerCreationForm, AccessCodeEmailForm, ClinicRegistrationForm

UserModel = get_user_model()


# Create your views here.
class BaseUserRegisterView(views.CreateView):
    """
        Newly created user will be handled by this view.

        If user is already registered, the dispatch method will handle the redirection of authenticated users.
        """
    # important here is to use form which is created by the user in forms.py
    redirect_authenticated_user = True

    @method_decorator(sensitive_post_parameters())  # not logging sensitive parameters
    @method_decorator(csrf_protect)  # enforces checking of CSRF token before the request is processed
    @method_decorator(never_cache)  # tells browsers not to store sensitive information
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        """
        All new user with never-existing-in-DB email is handled through form_valid(),
        after validation, the user is logged in automatically"""
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid

    def form_invalid(self, form):
        """
        if user is soft-deleted, they are no longer active, i.e. is_active = False, however, their details are still
        in the DB.
        The email will throw UNIQUE error, hence we need to bypass the email validator. This is done in the
        activate_soft_deleted_user()
        If the user is reactivated, this will redirect to success url and will not continue with form_invalid() method
        """
        reactivated = self.activate_soft_deleted_user(form)
        if reactivated:
            return redirect(self.get_success_url())

        return super().form_invalid(form)

    def activate_soft_deleted_user(self, form):
        try:
            user = UserModel.objects.get(email=form.data.get('email'), is_active=False)
        except UserModel.DoesNotExist:
            return False  # User does not exist or is not inactive

        password = form.cleaned_data.get('password1')
        user.set_password(password)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.is_active = True
        user.save()

        login(self.request, user)

        return True


class RegisterOwnerView(BaseUserRegisterView):
    form_class = OwnerCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')


class BaseLoginView(auth_views.LoginView):
    # this is needed to redirect the user out of the login page
    redirect_authenticated_user = True

    def form_valid(self, form):
        # attempting to clear the messages
        storage = messages.get_messages(self.request)
        storage.used = True
        return super().form_valid(form)


class LoginOwnerView(BaseLoginView):
    # this view requires template and 'next' to be used
    # 'next' is defined in settings.py LOGIN_REDIRECT_URL using reverse_lazy
    template_name = 'accounts/login.html'

    def form_invalid(self, form):
        # this form handles error msgs upon passing invalid credentials and
        # can be used in the template as {{ messages }} tag
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class AccessCodeEmailView(views.FormView):
    template_name = 'accounts/access_code_email.html'  # Page with Access Code + Email fields
    form_class = AccessCodeEmailForm

    def form_valid(self, form):
        access_code = form.cleaned_data.get('access_code')
        email_data = form.cleaned_data.get('email')
        email = email_data['email']
        email_exists = email_data['exists']

        if email_exists:
            user = UserModel.objects.get(email=email)
            if not user.is_owner:
                # Redirect to password page if email exists and access code is valid
                return redirect(reverse_lazy('password-entry') + f'?email={email}&code={access_code}')
            else:
                # Add a message explaining why they were redirected
                messages.error(self.request, 'You cannot log in as a veterinarian.')
                # Redirect to index page
                return redirect(reverse_lazy('index'))
        else:
            # If email doesn’t exist but is valid, redirect to registration
            return redirect(reverse_lazy('clinic-register') + f'?email={email}&code={access_code}')

    def form_invalid(self, form):
        # If the form has errors, re-render it with the errors displayed
        return self.render_to_response(self.get_context_data(form=form))


class PasswordEntryView(BaseLoginView):
    template_name = 'accounts/password_entry.html'
    form_class = AuthenticationForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        # Automatically log the user in on successful authentication
        user = form.get_user()
        login(self.request, user)
        return redirect(reverse_lazy(
            'clinic-dashboard') + f'?code={self.request.GET.get('code')}')  # Redirect to dashboard or success page after login

    def get_initial(self):
        # Pre-fill the email field from the query parameter
        email = self.request.GET.get('email', '')
        return {'username': email}

    def get_form_kwargs(self):
        """Pass POST data to the form, including the pre-filled username from GET params."""
        kwargs = super().get_form_kwargs()

        # Only modify data if there's a POST request
        if self.request.method == "POST":
            data = kwargs.get('data', {}).copy()  # Get current POST data
            # Add or update 'username' with the 'email' GET parameter
            if 'username' not in data or not data['username']:
                data['username'] = self.request.GET.get('email', '')  # Inject 'email' as username
            kwargs['data'] = data  # Pass modified data back

        return kwargs


class ClinicRegistrationView(BaseUserRegisterView):
    form_class = ClinicRegistrationForm
    template_name = 'accounts/clinc-register.html'

    def get_initial(self):
        # Pre-fill the email field from the query parameter
        email = self.request.GET.get('email', '')
        return {'email': email}

    def get_success_url(self):
        return reverse_lazy('clinic-dashboard') + f'?code={self.request.GET.get("code")}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['code'] = self.request.GET.get('code')
        return context


def logout_view(request):
    logout(request)
    return redirect('index')
