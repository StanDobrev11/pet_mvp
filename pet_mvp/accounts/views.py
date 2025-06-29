from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.signing import Signer
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views import generic as views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from pet_mvp.access_codes.models import VetPetAccess
from pet_mvp.accounts.forms import OwnerCreateForm, AccessCodeEmailForm, ClinicRegistrationForm, OwnerEditForm
from pet_mvp.accounts.models import Clinic
from pet_mvp.notifications.tasks import send_user_registration_email, send_clinic_admin_approval_request_email, \
    send_clinic_owner_access_request_email, send_clinic_activation_email
from pet_mvp.pets.models import Pet

UserModel = get_user_model()
signer = Signer()


# Create your views here.

class BaseUserRegisterView(views.CreateView):
    """
        Newly created user will be handled by this view.

        If user is already registered, the dispatch method will handle the redirection of authenticated users.
        """
    # important here is to use form which is created by the user in forms.py
    redirect_authenticated_user = True

    def set_default_language(self):
        """ sets the default language to the model bss browser settings,
        returns lang param for further email dispatch """

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

        password = form.data.get('password1')
        user.set_password(password)
        owner = user.owner
        owner.first_name = form.data.get('first_name')
        owner.last_name = form.data.get('last_name')
        user.is_active = True
        owner.save()
        user.save()

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return True


class ClinicRegistrationView(BaseUserRegisterView):
    form_class = ClinicRegistrationForm
    template_name = 'accounts/clinic-register.html'
    success_url = reverse_lazy('clinic-login')

    def get_initial(self):
        return {
            'email': self.request.GET.get('email', ''),
        }


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['code'] = self.request.GET.get('code')
        return context

    def form_valid(self, form):
        """Handle clinic creation via the custom manager, set inactive, send notifications."""
        # Extract cleaned form data
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        name = form.cleaned_data['name']
        address = form.cleaned_data['address']
        phone_number = form.cleaned_data['phone_number']
        city = form.cleaned_data['city']
        country = form.cleaned_data['country']

        # Create user using custom manager (clinic is not active by default)
        user = UserModel.objects.create_clinic(
            email=email,
            password=password,
            name=name,
            address=address,
            phone_number=phone_number,
            city=city,
            country=country,
            is_active=False  # ensure explicitly set to inactive
        )

        # Store access code
        code = self.request.GET.get('code')
        self.request.session['code'] = code

        try:
            pet = Pet.objects.get(pet_access_code__code=code)
            owners = pet.owners.all()
        except Pet.DoesNotExist:
            messages.error(self.request, _("Invalid access code."))
            return redirect('index')

        # Send email to pet owner(s)
        approval_url = self.request.build_absolute_uri(
            reverse('approve-temp-clinic') + f'?clinic_id={user.id}&pet_id={pet.id}'
        )
        for owner in owners:
            send_clinic_owner_access_request_email(
                user_owner=owner,
                user_clinic=user,
                pet=pet,
                url=approval_url,
                lang=owner.default_language
            )

        # Send email to admin
        send_clinic_admin_approval_request_email(user_clinic=user, pet=pet)

        messages.success(self.request, _(
            "Your registration was successful. An approval request has been sent to the pet's owner."))

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class RegisterOwnerView(BaseUserRegisterView):
    form_class = OwnerCreateForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        """
        Create the user using the custom manager to ensure Owner profile is created.
        Then log them in, send welcome email, and proceed.
        """
        # Extract data
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        phone_number = form.cleaned_data['phone_number']
        city = form.cleaned_data['city']
        country = form.cleaned_data['country']

        # Create user using custom method (this also creates Owner)
        user = UserModel.objects.create_owner(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            city=city,
            country=country,
        )

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        self.object = user

        lang = self.set_default_language()
        send_user_registration_email(user, lang)

        return redirect(self.get_success_url())


class BaseLoginView(auth_views.LoginView):
    # this is needed to redirect the user out of the login page
    redirect_authenticated_user = True
    template_name = 'accounts/login.html'

    def get_success_url(self):
        if self.request.user.is_owner:
            return reverse_lazy('dashboard')

        if self.request.user.clinic.is_approved and self.request.user.is_active:
            return reverse_lazy('clinic-dashboard')

        messages.error(self.request, _('Must be a registered pet owner or active and approved vet clinic'))
        return reverse_lazy('index')

    def form_valid(self, form):
        # check for clinic object
        user_email = form.cleaned_data.get('username')

        # normalize email address
        user_email = user_email.lower()

        user = UserModel.objects.get(email=user_email)

        # redirect bss type of clinic
        if hasattr(user, 'clinic'):
            if user.clinic.is_approved:
                self.success_url = reverse_lazy('clinic-dashboard')

            elif user.is_active:
                messages.error(self.request, _('Please login using the access code'))
                return redirect('clinic-login')

            else:
                messages.error(self.request, _('You must be approved by the pet\'s owner first'))
                return redirect('index')

        # attempting to clear the messages
        storage = messages.get_messages(self.request)
        storage.used = True
        return super().form_valid(form)

    def form_invalid(self, form):
        # this form handles error msgs upon passing invalid credentials and
        # can be used in the template as {{ messages }} tag
        messages.error(self.request, _('Invalid email or password.'))
        return super().form_invalid(form)


class AccessCodeEmailView(views.FormView):
    template_name = 'accounts/access_code_email.html'
    form_class = AccessCodeEmailForm

    def form_valid(self, form):
        access_code = form.cleaned_data.get('access_code')
        email = form.cleaned_data.get('email')['email']

        # Lookup pet & owner
        try:
            pet = Pet.objects.get(pet_access_code__code=access_code)
            owners = pet.owners.all()
        except Pet.DoesNotExist:
            messages.error(self.request, _("Invalid access code."))
            return self.form_invalid(form)

        # Lookup clinic user
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            messages.info(self.request, _(
                "This clinic is not in the system. "
                "Please complete the registration form below to request temporary access."))
            return redirect(f"{reverse('clinic-register')}?email={email}&code={access_code}")

        # Owners cannot act as clinics
        if hasattr(user, 'owner'):
            messages.error(self.request, _("Owners cannot access the website as vets."))
            return self.form_invalid(form)

        # approved is considered a clinic authorized by the admin, no access to pets.If an owner is providing access
        # code for the first time to that clinic, clinic self-activation will take place

        # approved clinic has 2 options - either wait for admin approval or enter pet access code and receive the
        # self-activation email

        # activated is a clinic that is authorized by user to access temporary their pet
        # approved and activated is a clinic with full and permanent access

        # approved and activated - simple login with password
        if user.clinic.is_approved and user.is_active:
            return redirect(f"{reverse('password-entry')}?email={email}&code={access_code}")

        # approved but not yet activated -> send mail clinic to self activate using the link
        elif user.clinic.is_approved:

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = self.request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_clinic_activation_email(
                user=user,
                lang=user.default_language,
                url=activation_url,
            )
            messages.success(self.request, _(
                "Activation email sent. Please check your inbox to confirm your clinic access."))
            return redirect('clinic-login')

        # not approved, newly created, but owner activated -> password entry
        elif user.is_active:
            return redirect(f"{reverse('password-entry')}?email={email}&code={access_code}")

        # not approved and not activated but existing -> send email to owner for temp activation
        else:
            activation_url = self.request.build_absolute_uri(
                reverse('approve-temp-clinic') + f'?clinic_id={user.id}&pet_id={pet.id}')

            for owner in owners:
                send_clinic_owner_access_request_email(
                    user_owner=owner,
                    user_clinic=user,
                    pet=pet,
                    url=activation_url,
                    lang=owner.default_language
                )

            messages.info(self.request, _(
                "This clinic is awaiting approval. An access request was sent to the pet's owner."))
            return redirect('clinic-login')

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return self.render_to_response(self.get_context_data(form=form))


class ApproveTempClinicView(views.View):

    def get(self, request):
        clinic_id = request.GET.get('clinic_id')
        pet_id = request.GET.get('pet_id')

        if not clinic_id or not pet_id:
            messages.error(request, _("Invalid approval request."))
            return redirect('index')

        # Get clinic and pet
        user = get_object_or_404(UserModel, id=clinic_id, is_owner=False)
        pet = get_object_or_404(Pet, id=pet_id)

        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, _(
                f"Access for clinic '{user.clinic.name}' has been activated. They can now manage records for '{pet.name}'."
            ))
        else:
            messages.info(request, _("This clinic was already activated."))

        return redirect('index')


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        return context

    def form_valid(self, form):
        # Save the new password
        response = super().form_valid(form)

        # Activate vet clinic on first-time activation
        if not self.user.is_owner and not self.user.is_active:
            self.user.is_active = True
            self.user.save()

        messages.success(self.request, _("Password set successfully. Please continue."))
        return response

    def get_success_url(self):
        # Override default to prevent redirect to /set-password/
        return reverse('login' if self.user.is_owner else 'clinic-login')


class PasswordEntryView(BaseLoginView):
    template_name = 'accounts/password_entry.html'
    form_class = AuthenticationForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.get_user()
        code = self.request.GET.get('code')

        # Log in the user
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Get the pet ID
        pet = Pet.objects.get(pet_access_code__code=code)

        VetPetAccess.objects.update_or_create(
            vet=user,
            pet=pet,
            defaults={
                # 'expires_at': timezone.now() + timedelta(minutes=10),
                # adding infinite exp for the code for testing
                'expires_at': timezone.now() + timedelta(days=240),
                'granted_by': 'access code'
            }
        )
        # Create the redirect response
        if user.clinic.is_approved:
            response = redirect('clinic-dashboard')
        else:
            response = redirect(reverse_lazy('pet-details', kwargs={'pk': pet.id}))

        # Set the cookie on the response
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


class OwnerDetailsView(views.DetailView):
    """
    View for displaying the details of a pet owner.
    """
    model = UserModel
    template_name = 'accounts/owner_details.html'
    context_object_name = 'owner'


class OwnerEditView(views.UpdateView):
    """
    View for editing the details of a pet owner.
    """
    model = UserModel
    form_class = OwnerEditForm
    template_name = 'accounts/owner_edit.html'
    context_object_name = 'owner'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_owner:
            if request.method == 'GET':
                return super().get(request, *args, **kwargs)
            else:
                return super().post(request, *args, **kwargs)
        else:
            messages.error(request, _("You are not allowed to edit the owner."))
            return redirect('clinic-dashboard')

    def get_success_url(self):
        return reverse_lazy('owner-details', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Disable email editing if social account exists
        if self.request.user.socialaccount_set.filter(provider='google').exists():
            form.fields['email'].disabled = True
        return form


class ClinicDetailsView(views.DetailView):
    model = Clinic
    template_name = 'accounts/clinic_details.html'
    context_object_name = 'clinic'
