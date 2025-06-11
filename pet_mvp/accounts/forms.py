from django.contrib.auth import forms as auth_forms, get_user_model
from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.models import Clinic, Owner
from pet_mvp.accounts.validators import normalize_bulgarian_phone
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class BaseOwnerForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))

    class Meta:
        model = UserModel
        fields = ('email', 'phone_number', 'city', 'country')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'instance' in kwargs and kwargs['instance']:
            instance = kwargs['instance']
            profile_instance = getattr(instance, 'owner', None)
        else:
            profile_instance = kwargs.pop('profile_instance', None)


        if profile_instance:
            self.fields['first_name'].initial = profile_instance.first_name
            self.fields['last_name'].initial = profile_instance.last_name

        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = str(field.label).capitalize()

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number')
        if value:
            return normalize_bulgarian_phone(value)
        return value

    def save(self, commit=True):
        user = super().save(commit)
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        if hasattr(user, 'owner'):
            profile = user.owner
        else:
            profile = Owner(user=user)

        profile.first_name = first_name
        profile.last_name = last_name
        if commit:
            profile.save()

        return user


class OwnerCreateForm(auth_forms.UserCreationForm, BaseOwnerForm):
    class Meta(auth_forms.UserCreationForm.Meta, BaseOwnerForm.Meta):
        model = UserModel
        fields = ('email', 'phone_number', 'city', 'country', 'first_name', 'last_name')


class OwnerEditForm(BaseOwnerForm):
    pass


class ClinicRegistrationForm(auth_forms.UserCreationForm):
    name = forms.CharField(label=_("Clinic name"))
    address = forms.CharField(label=_("Clinic address"))

    class Meta:
        model = UserModel
        fields = ['email', 'phone_number', 'city', 'country', 'name', 'address']

        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.instance.is_owner = False  # enforce clinic flag
            self.instance.is_clinic = True

        for field_name, field in self.fields.items():
            if field_name == 'password1':
                field.widget.attrs['placeholder'] = _('Enter a password')
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = _('Repeat the password')
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = _('Phone number (e.g. 0887123456)')
            else:
                placeholder = field.label or self._meta.model._meta.get_field(field_name).verbose_name
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number')
        if value:
            return normalize_bulgarian_phone(value)
        return value

    def save(self, commit=True):
        user = super().save(commit=commit)
        name = self.cleaned_data.get('name')
        address = self.cleaned_data.get('address')

        profile, created = Clinic.objects.get_or_create(user=user)
        profile.name = name
        profile.address = address
        if commit:
            profile.save()

        return user


class AccessCodeEmailForm(forms.Form):
    access_code = forms.CharField(label=_("Access Code"), required=True)
    email = forms.EmailField(label=_("Email Address"), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            translated_label = _(field.label)
            field.widget.attrs['placeholder'] = translated_label

    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code')
        pet_exists = Pet.objects.filter(
            pet_access_code__code=access_code).exists()
        if not pet_exists:
            raise forms.ValidationError(_('Invalid Access Code'))
        return access_code

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)  # Ensures a properly formatted email address
        except forms.ValidationError:
            raise forms.ValidationError(_('Enter a valid email address.'))

        # Verify if email exists in the database
        email_exists = UserModel.objects.filter(email=email).exists()
        return {'email': email, 'exists': email_exists}
