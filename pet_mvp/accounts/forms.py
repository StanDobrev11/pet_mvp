from django.contrib.auth import forms as auth_forms, get_user_model

UserModel = get_user_model()


class OwnerCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model=UserModel
        fields=('email', 'first_name', 'last_name', 'phone_number', 'city')


class ClinicCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['email', 'clinic_name', 'clinic_address', 'phone_number', 'city', 'country']
