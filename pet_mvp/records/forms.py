from pet_mvp.drugs.models import Vaccine, Drug
from pet_mvp.records.models import VaccinationRecord, MedicationRecord

from django import forms
from django.utils.translation import gettext_lazy as _


class VaccineRecordAddForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        exclude = ['pet']  # Exclude the `pet` field, it will be assigned automatically

    vaccine = forms.ModelChoiceField(
        queryset=Vaccine.objects.all(),
        label=_('Select Vaccine'),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )


class TreatmentRecordAddForm(forms.ModelForm):
    class Meta:
        model = MedicationRecord
        exclude = ['pet']  # Exclude the `pet` field, it will be assigned automatically

    medication = forms.ModelChoiceField(
        queryset=Drug.objects.all(),
        label=_('Select Medication/Treatment'),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )