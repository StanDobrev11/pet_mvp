from pet_mvp.pets.models import BaseMarking, Transponder, Tattoo, Pet
from django.utils.translation import gettext as _
from django import forms
from django.utils.translation import gettext_lazy as _

from pet_mvp.pets.validators import validate_passport_number


class PetEditForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['passport_number', 'photo', 'current_weight']


class PetAddForm(forms.ModelForm):

    class Meta:
        model = Pet
        exclude = [
            'owners',
            'can_add_vaccines',
            'pending_owners',
            'name', 'color','features',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Breed dropdown setup
        if self.instance.pk and self.instance.species:
            self.fields['breed'].widget = forms.Select(
                choices=self.instance.get_breed_choices())
        elif self.data.get('species'):
            species = self.data.get('species')
            if species == 'dog':
                self.fields['breed'].widget = forms.Select(choices=Pet.DOG_BREED_CHOICES)
            elif species == 'cat':
                self.fields['breed'].widget = forms.Select(choices=Pet.CAT_BREED_CHOICES)
        else:
            self.fields['breed'].widget = forms.Select(choices=[])

        # Placeholder logic
        for field_name, field in self.fields.items():
            if field_name == 'date_of_birth':
                field.widget = forms.DateInput(attrs={'type': 'date'})
                field.help_text = _('Date of birth')
            elif field_name == 'passport_number':
                field.widget.attrs['placeholder'] = _('Format BG01VPXXXXXX or blank')
                field.widget.attrs['required'] = False
            elif '_en' in field_name:
                base_field_name = field_name.replace('_en', '')
                base_verbose = self._meta.model._meta.get_field(base_field_name).verbose_name
                field.widget.attrs['placeholder'] = f"{base_verbose} ({_('in English')})"
                field.widget.attrs['required'] = True
            elif '_bg' in field_name:
                base_field_name = field_name.replace('_bg', '')
                base_verbose = self._meta.model._meta.get_field(base_field_name).verbose_name
                field.widget.attrs['placeholder'] = f"{base_verbose} ({_('in Bulgarian')})"
                field.widget.attrs['required'] = True
            elif field_name == 'current_weight':
                field.widget.attrs['placeholder'] = _('Current weight in kgs')
            else:
                field.widget.attrs['placeholder'] = str(field.label).capitalize()

    def clean_passport_number(self):
        value = self.cleaned_data.get('passport_number')
        if value:
            return validate_passport_number(value)

        return None

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['name_en', 'name_bg', 'color_en', 'color_bg']
        if not all(cleaned_data[field] for field in required_fields):
                raise forms.ValidationError(_('This field is required.'))

        return cleaned_data

class MarkingAddForm(forms.Form):
    MARKING_CHOICES = [
        ('Transponder', 'Transponder'),
        ('Tattoo', 'Tattoo'),
    ]

    marking_type = forms.ChoiceField(
        choices=MARKING_CHOICES,
        label='Marking Type',
        widget=forms.RadioSelect
    )

    code = forms.CharField(
        max_length=BaseMarking.CODE_MAX_LENGTH,
        label='Code'
    )

    date_of_application = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date of Application'
    )

    date_of_reading = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date of Reading'
    )

    location = forms.CharField(
        max_length=BaseMarking.LOCATION_MAX_LENGTH,
        label='Location'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and kwargs['initial'].get('marking_type') == 'Transponder':
            self.fields['date_of_application'].required = False
            self.fields['date_of_reading'].required = False

    def clean(self):
        cleaned_data = super().clean()
        marking_type = cleaned_data.get('marking_type')
        code = cleaned_data.get('code')

        if marking_type == 'Transponder':
            from .validators import validate_transponder_code
            try:
                validate_transponder_code(code)
            except forms.ValidationError as e:
                self.add_error('code', e)

        return cleaned_data

    def save(self, pet):
        marking_type = self.cleaned_data['marking_type']
        marking_class = Transponder if marking_type == 'Transponder' else Tattoo

        marking = marking_class(
            pet=pet,
            code=self.cleaned_data['code'],
            date_of_application=self.cleaned_data['date_of_application'],
            date_of_reading=self.cleaned_data['date_of_reading'],
            location=self.cleaned_data['location']
        )
        marking.save()
        return marking


class AddExistingPetForm(forms.Form):
    passport_number = forms.CharField(
        label=_("Passport number"),
        widget=forms.TextInput(attrs={'placeholder': _('Format BG01VPXXXXXX')}),
        validators=[validate_passport_number]
    )