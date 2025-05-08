from sys import prefix

from pet_mvp.drugs.models import Vaccine, Drug, FecalTest, UrineTest, BloodTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

from django import forms
from django.utils.translation import gettext_lazy as _


class VaccinationRecordForm(forms.ModelForm):
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


class MedicationRecordForm(forms.ModelForm):
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


class BloodTestForm(forms.ModelForm):
    class Meta:
        model = BloodTest
        fields = ['name', 'date_conducted', 'result', 'white_blood_cells',
                  'red_blood_cells', 'hemoglobin', 'platelets', 'additional_notes']
        widgets = {
            # 'date_conducted': forms.DateInput(attrs={'type': 'date'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class UrineTestForm(forms.ModelForm):
    class Meta:
        model = UrineTest
        fields = ['name', 'date_conducted', 'result', 'color', 'clarity',
                  'ph', 'specific_gravity', 'protein', 'glucose',
                  'white_blood_cells', 'red_blood_cells', 'additional_notes']
        widgets = {
            'date_conducted': forms.DateInput(attrs={'type': 'date'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class FecalTestForm(forms.ModelForm):
    class Meta:
        model = FecalTest
        fields = ['name', 'date_conducted', 'result', 'consistency',
                  'parasites_detected', 'parasite_type', 'blood_presence', 'additional_notes']
        widgets = {
            'date_conducted': forms.DateInput(attrs={'type': 'date'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2}),
        }


class MedicalExaminationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalExaminationRecord
        exclude = ['pet', 'vaccinations', 'medications', 'blood_test', 'urine_test', 'fecal_test']

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
