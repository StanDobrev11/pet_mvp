from pet_mvp.records.models import VaccinationRecord

from django import forms

class VaccineRecordAddForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        fields = '__all__'
