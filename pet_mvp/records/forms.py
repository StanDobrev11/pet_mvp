from datetime import timedelta
from sys import prefix

from pet_mvp.drugs.models import Vaccine, Drug, FecalTest, UrineTest, BloodTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

from django import forms
from django.utils.translation import gettext_lazy as _


class VaccinationRecordForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        exclude = ['pet']

    def __init__(self, *args, pet=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter vaccines by species if pet is given
        if pet:
            species = pet.species if hasattr(pet, 'species') else pet
            self.fields['vaccine'].queryset = Vaccine.objects.filter(
                suitable_for=species.lower()
            )
        else:
            self.fields['vaccine'].queryset = Vaccine.objects.none()

        self.fields['vaccine'].label = _('Select Vaccine')
        self.fields['vaccine'].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_vaccine',
        })

        # Style all fields and set help texts
        for field_name in self.fields:
            field = self.fields[field_name]

            if field_name in ['date_of_vaccination']:
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = _('Date of vaccination')
            elif field_name == 'valid_until':
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = _('Valid until date')
            elif field_name == 'manufacture_date':
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = _('Manufacture date')
            elif field_name == 'valid_from':
                field.widget = forms.DateInput(attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'readonly': 'readonly',
                    'style': 'background-color: #e9ecef; cursor: not-allowed;',
                })
                field.help_text = _('This field is automatically filled for Rabies vaccine (21 days after vaccination).')
            elif field_name != 'vaccine':
                placeholder = self._meta.model._meta.get_field(field_name).verbose_name
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': str(placeholder).capitalize()
                })
    def clean(self):
        cleaned_data = super().clean()
        vaccine = cleaned_data.get("vaccine")
        date_of_vaccination = cleaned_data.get("date_of_vaccination")

        if vaccine and "rabies" in vaccine.name.lower() and date_of_vaccination:
            cleaned_data["valid_from"] = date_of_vaccination + timedelta(days=21)

        return cleaned_data

class MedicationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicationRecord
        exclude = ['pet']

    def __init__(self, *args, pet=None, **kwargs):
        super().__init__(*args, **kwargs)

        if pet:
            species = pet.species if hasattr(
                pet, 'species') else pet  # assume string if not model
            self.fields['medication'].queryset = Drug.objects.filter(
                suitable_for=species.lower())
        else:
            self.fields['medication'].queryset = Drug.objects.none()

        self.fields['medication'].label = _('Select Medication/Treatment')
        self.fields['medication'].widget.attrs.update(
            {'class': 'form-control', 'id': 'id_medication'})

        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name == 'date':
                field.widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = _('Date of intake')
            elif field_name == 'valid_until':
                field.widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = _('Valid until date')
            elif field_name == 'time':
                field.widget = forms.TimeInput(
                    attrs={'type': 'time', 'class': 'form-control'})
                field.help_text = _('Time of intake')
            else:
                placeholder = self._meta.model._meta.get_field(
                    field_name).verbose_name
                field.widget.attrs['placeholder'] = str(
                    placeholder).capitalize()

    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get("medication")
        custom_name = cleaned_data.get("custom_medication")

        if medication is None and not custom_name:
            raise forms.ValidationError(
                _("Please select a medication or enter a custom one."))

        return cleaned_data


class BloodTestForm(forms.ModelForm):
    class Meta:
        model = BloodTest
        fields = ['date_conducted', 'result', 'white_blood_cells',
                  'red_blood_cells', 'hemoglobin', 'platelets', 'additional_notes']
        widgets = {
            'result': forms.TextInput(attrs={'class': 'form-control'}),
            'date_conducted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class UrineTestForm(forms.ModelForm):
    class Meta:
        model = UrineTest
        fields = ['date_conducted', 'result', 'color', 'clarity',
                  'ph', 'specific_gravity', 'protein', 'glucose',
                  'white_blood_cells', 'red_blood_cells', 'additional_notes']
        widgets = {
            'result': forms.TextInput(attrs={'class': 'form-control'}),
            'date_conducted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class FecalTestForm(forms.ModelForm):
    class Meta:
        model = FecalTest
        fields = ['date_conducted', 'result', 'consistency',
                  'parasites_detected', 'parasite_type', 'blood_presence', 'additional_notes']
        widgets = {
            'result': forms.TextInput(attrs={'class': 'form-control'}),
            'date_conducted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class MedicalExaminationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalExaminationRecord
        exclude = ['pet', 'clinic', 'vaccinations', 'medications',
                   'blood_test', 'urine_test', 'fecal_test']


VaccineFormSet = forms.modelformset_factory(
    VaccinationRecord,
    form=VaccinationRecordForm,
    extra=0,
    can_delete=True
)

TreatmentFormSet = forms.modelformset_factory(
    MedicationRecord,
    form=MedicationRecordForm,
    extra=0,
    can_delete=True
)
