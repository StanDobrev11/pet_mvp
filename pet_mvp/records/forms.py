from pet_mvp.drugs.models import Vaccine, Drug, FecalTest, UrineTest, BloodTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

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


class ExaminationForm(forms.ModelForm):
    # Fields for related tests
    blood_test_needed = forms.BooleanField(required=False, label=_("Add Blood Test"))
    urine_test_needed = forms.BooleanField(required=False, label=_("Add Urine Test"))
    fecal_test_needed = forms.BooleanField(required=False, label=_("Add Fecal Test"))

    class Meta:
        model = MedicalExaminationRecord
        exclude = ['medication', 'vaccination', 'blood_test', 'urine_test', 'fecal_test']
        widgets = {
            'date_of_entry': forms.DateInput(attrs={'type': 'date'}),
            'reason_for_visit': forms.Textarea(attrs={'rows': 3}),
            'general_health': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment_performed': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        pet_id = kwargs.pop('pet_id', None)
        super(ExaminationForm, self).__init__(*args, **kwargs)
        if pet_id:
            self.fields['pet'].initial = pet_id
            self.fields['pet'].widget = forms.HiddenInput()


class VaccinationRecordForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        fields = [
            'vaccine', 'batch_number', 'manufacturer',
            'manufacture_date', 'date_of_vaccination',
            'valid_from', 'valid_until'
        ]
        widgets = {
            'manufacture_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_vaccination': forms.DateInput(attrs={'type': 'date'}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }


class MedicationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicationRecord
        fields = [
            'medication', 'manufacturer', 'date', 'time',
            'dosage', 'valid_until'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }


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
