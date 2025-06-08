from datetime import timedelta

from pet_mvp.drugs.models import Vaccine, Drug, FecalTest, UrineTest, BloodTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms.models import BaseModelFormSet


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
                field.help_text = _(
                    'This field is automatically filled for Rabies vaccine (21 days after vaccination).')
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


class BaseTestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            placeholder = self._meta.model._meta.get_field(field_name).verbose_name

            if field_name == 'result':
                field.widget = forms.TextInput(attrs={'class': 'form-control'})
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()
            elif field_name == 'date_conducted':
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
            elif field_name == 'additional_notes':
                field.widget = forms.Textarea(attrs={'rows': 2})
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()
            else:
                field.widget.attrs['placeholder'] = str(placeholder).capitalize()

class BloodTestForm(BaseTestForm):
    class Meta:
        model = BloodTest
        fields = ['date_conducted', 'result', 'white_blood_cells',
                  'red_blood_cells', 'hemoglobin', 'platelets', 'additional_notes']



class UrineTestForm(BaseTestForm):
    class Meta:
        model = UrineTest
        fields = ['date_conducted', 'result', 'color', 'clarity',
                  'ph', 'specific_gravity', 'protein', 'glucose',
                  'white_blood_cells', 'red_blood_cells', 'additional_notes']


class FecalTestForm(BaseTestForm):
    class Meta:
        model = FecalTest
        fields = ['date_conducted', 'result', 'consistency',
                  'parasites_detected', 'parasite_type', 'blood_presence', 'additional_notes']

    boolean_select_fields = ['parasites_detected', 'blood_presence']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            placeholder = self._meta.model._meta.get_field(field_name).verbose_name

            if field_name in self.boolean_select_fields:
                field.widget = forms.Select(
                    choices=[('true', _('Yes')), ('false', _('No'))],
                    attrs={'class': 'form-control'}
                )
                self.initial[field_name] = 'false'

            elif field_name == 'parasite_type':
                field.widget = forms.TextInput(
                    attrs={
                        'readonly': 'readonly',
                        'class': 'form-control d-none',
                        'placeholder': str(placeholder).capitalize()
                    }
                )

    def clean_parasites_detected(self):
        return self.cleaned_data.get('parasites_detected') == 'true'

    def clean_blood_presence(self):
        return self.cleaned_data.get('blood_presence') == 'true'

    def clean_parasite_type(self):
        if self.cleaned_data.get('parasites_detected'):
            return self.cleaned_data.get('parasite_type')
        return None


class MedicalExaminationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalExaminationRecord
        exclude = ['pet', 'clinic', 'vaccinations', 'medications',
                   'blood_test', 'urine_test', 'fecal_test']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name == 'date_of_entry':
                field.widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'})
            elif field_name == 'follow_up':
                field.widget = forms.Select(
                    choices=[('true', _('Yes')), ('false', _('No'))],
                    attrs={'class': 'form-select'}
                )
                self.initial['follow_up'] = 'false'
            else:
                placeholder = self._meta.model._meta.get_field(
                    field_name).verbose_name
                field.widget.attrs['placeholder'] = str(
                    placeholder).capitalize()

    def clean_follow_up(self):
        value = self.cleaned_data.get('follow_up')
        if value == 'true':
            return True
        else:
            return False


class BaseFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        self.pet = kwargs.pop('pet', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['pet'] = self.pet
        return super()._construct_form(i, **kwargs)

    @property
    def empty_form(self):
        form = self.form(
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            pet=self.pet,  # inject pet
        )
        self.add_fields(form, None)
        return form


VaccineFormSet = forms.modelformset_factory(
    VaccinationRecord,
    form=VaccinationRecordForm,
    extra=0,
    can_delete=True,
    formset=BaseFormSet,
)

TreatmentFormSet = forms.modelformset_factory(
    MedicationRecord,
    form=MedicationRecordForm,
    extra=0,
    can_delete=True,
    formset=BaseFormSet,
)
