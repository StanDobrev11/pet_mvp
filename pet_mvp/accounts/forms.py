from django.contrib.auth import forms as auth_forms, get_user_model
from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext as _
from pet_mvp.accounts.validators import normalize_bulgarian_phone
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class OwnerCreationForm(auth_forms.UserCreationForm):

    class Meta:
        model = UserModel
        fields = ('email', 'first_name', 'last_name',
                  'phone_number', 'city', 'country')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]

            if field_name == 'password1':
                field.widget.attrs['placeholder'] = _('Enter a password')
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = _('Repeat the password')
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = _('Phone number (e.g. 0887123456)')
            else:
                placeholder = self._meta.model._meta.get_field(field_name).verbose_name
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()


class ClinicRegistrationForm(auth_forms.UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['email', 'clinic_name', 'clinic_address',
                  'phone_number', 'city', 'country']

        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure is_owner defaults to False on the instance
        if self.instance:  # If we have a model instance, set is_owner to False here
            self.instance.is_owner = False
        
        for field_name in self.fields:
            field = self.fields[field_name]

            if field_name == 'password1':
                field.widget.attrs['placeholder'] = _('Enter a password')
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = _('Repeat the password')
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = _('Phone number (e.g. 0887123456)')
            else:
                placeholder = self._meta.model._meta.get_field(field_name).verbose_name
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()
                
    def clean_phone_number(self):

        value = self.cleaned_data.get('phone_number')
        if not value:
            return
        return normalize_bulgarian_phone(value)
    

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
