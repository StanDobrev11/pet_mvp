from django import forms

from pet_mvp.pets.models import Pet, BaseMarking, Transponder, Tattoo


class PetEditForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['photo', 'current_weight']


class PetAddForm(forms.ModelForm):
    class Meta:
        model = Pet
        exclude = ['owners']


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
