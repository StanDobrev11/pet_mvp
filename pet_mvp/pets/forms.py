from django import forms

from pet_mvp.pets.models import Pet, BaseMarking, Transponder, Tattoo


class PetEditForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['photo', 'current_weight']


class PetAddForm(forms.ModelForm):
    class Meta:
        model = Pet
        exclude = [
            'owners', 'can_add_vaccines', 'can_add_treatments',
            'name',
            'color',
            'features',
            'pending_owners',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial breed choices based on current species value
        if self.instance.pk and self.instance.species:
            # For existing pets, use the species from the instance
            self.fields['breed'].widget = forms.Select(
                choices=self.instance.get_breed_choices())
        elif self.data.get('species'):
            # For form submissions, use the species from the submitted data
            species = self.data.get('species')
            if species == 'dog':
                self.fields['breed'].widget = forms.Select(
                    choices=Pet.DOG_BREED_CHOICES)
            elif species == 'cat':
                self.fields['breed'].widget = forms.Select(
                    choices=Pet.CAT_BREED_CHOICES)
        else:
            # Default to empty choices if no species is selected
            self.fields['breed'].widget = forms.Select(choices=[])


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


class AddExistingPetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['passport_number']
        widgets = {
            'passport_number': forms.TextInput(attrs={'maxlength': 20}),
        }
