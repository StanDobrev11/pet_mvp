from django.contrib.auth import forms as auth_forms, get_user_model
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.utils.translation import gettext as _
from pet_mvp.access_codes.models import PetAccessCode
from pet_mvp.accounts.validators import validate_bulgarian_phone
from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class OwnerCreationForm(auth_forms.UserCreationForm):
    
    phone_number = forms.CharField(
        max_length=9,
        validators=[validate_bulgarian_phone],
        widget=forms.TextInput(attrs={
            'placeholder': _('Format: 0887123456'),
            'pattern': '[0-9]{10}',
            'class': 'form-control',
        }),
    )
    
    class Meta:
        model = UserModel
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'country')


    
    
class ClinicRegistrationForm(auth_forms.UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['email', 'clinic_name', 'clinic_address', 'phone_number', 'city', 'country']

        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure is_owner defaults to False on the instance
        if self.instance:  # If we have a model instance, set is_owner to False here
            self.instance.is_owner = False


class AccessCodeEmailForm(forms.Form):
    access_code = forms.CharField(label="Access Code", required=True)
    email = forms.EmailField(label="Email Address", required=True)

    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code')
        pet_exists = Pet.objects.filter(pet_access_code__code=access_code).exists()
        if not pet_exists:
            raise forms.ValidationError('Invalid Access Code')
        return access_code

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)  # Ensures a properly formatted email address
        except forms.ValidationError:
            raise forms.ValidationError('Enter a valid email address.')

        # Verify if email exists in the database
        email_exists = UserModel.objects.filter(email=email).exists()
        return {'email': email, 'exists': email_exists}
