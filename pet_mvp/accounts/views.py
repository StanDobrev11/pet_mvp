from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic as views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from pet_mvp.accounts.forms import OwnerCreationForm, AccessCodeEmailForm, ClinicRegistrationForm
from pet_mvp.notifications.tasks import send_user_registration_email
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


# Create your views here.
class BaseUserRegisterView(views.CreateView):
    """
        Newly created user will be handled by this view.

        If user is already registered, the dispatch method will handle the redirection of authenticated users.
        """
    # important here is to use form which is created by the user in forms.py
    redirect_authenticated_user = True

    def set_default_language(self):
        """ sets the default language to the model bss browser settings, returns lang param for further email dispatch """

        # get the language from the django_language cookie
        lang = self.request.COOKIES.get("django_language", "en")
        # set the language to the model
        self.object.default_language = lang
        # send successful registration message
        return lang

    # not logging sensitive parameters
    @method_decorator(sensitive_post_parameters())
    # enforces checking of CSRF token before the request is processed
    @method_decorator(csrf_protect)
    # tells browsers not to store sensitive information
    @method_decorator(never_cache)
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
        after validation, the user is logged in automatically
        Added mail sending on creation"""
        valid = super().form_valid(form)
        login(self.request, self.object)

        # get the user
        user = self.object
        # set and get the language param
        lang = self.set_default_language()
        # send user welcome email
        send_user_registration_email(user, lang)
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
            user = UserModel.objects.get(
                email=form.data.get('email'), is_active=False)
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


class ClinicRegistrationView(BaseUserRegisterView):
    form_class = ClinicRegistrationForm
    template_name = 'accounts/clinc-register.html'

    def get_initial(self):
        # Pre-fill the email field from the query parameter
        email = self.request.GET.get('email', '')
        return {'email': email}

    def get_success_url(self):
        code = self.request.GET.get('code')
        pet_id = Pet.objects.get(pet_access_code__code=code).pk
        return reverse_lazy('pet-details', kwargs={'pk': pet_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['code'] = self.request.GET.get('code')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # response.set_cookie('code', self.request.GET.get('code'))
        login(self.request, self.object)
        self.request.session['code'] = self.request.GET.get('code')

        # set and get the language param
        lang = self.set_default_language()
        # TODO create send_clinic_registration_email
        
        return response


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
    # Page with Access Code + Email fields
    template_name = 'accounts/access_code_email.html'
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
                url = reverse_lazy('password-entry') + \
                    f'?email={email}&code={access_code}'
                return redirect(url)
            else:
                # Add a message explaining why they were redirected
                messages.error(
                    self.request, 'You cannot log in as a veterinarian.')
                # Redirect to index page
                return redirect(reverse_lazy('index'))
        else:
            # If email doesn’t exist but is valid, redirect to registration
            url = reverse_lazy('clinic-register') + \
                f'?email={email}&code={access_code}'
            return redirect(url)

    def form_invalid(self, form):
        # If the form has errors, re-render it with the errors displayed
        return self.render_to_response(self.get_context_data(form=form))


class PasswordEntryView(BaseLoginView):
    template_name = 'accounts/password_entry.html'
    form_class = AuthenticationForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.get_user()
        code = self.request.GET.get('code')

        # Log in the user
        login(self.request, user)

        # Get the pet ID
        pet_id = Pet.objects.get(pet_access_code__code=code).pk

        # Create the redirect response
        response = redirect(reverse_lazy('pet-details', kwargs={'pk': pet_id}))

        # Set the cookie on the response
        # response.set_cookie('code', code)
        self.request.session['code'] = code

        return response

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
                data['username'] = self.request.GET.get(
                    'email', '')  # Inject 'email' as username
            kwargs['data'] = data  # Pass modified data back

        return kwargs


def logout_view(request):
    logout(request)

    return redirect('index')
