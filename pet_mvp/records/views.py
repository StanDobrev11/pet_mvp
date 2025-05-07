from abc import ABC, abstractmethod
from django.contrib import messages
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic as views

from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import VaccineRecordAddForm, TreatmentRecordAddForm, FecalTestForm, UrineTestForm, \
    BloodTestForm, VaccinationRecordForm, MedicationRecordForm, ExaminationForm
from pet_mvp.records.models import VaccinationRecord, MedicalExaminationRecord, MedicationRecord


# Create your views here.
class RecordListView(views.ListView):
    template_name = 'records/record_list.html'

    def get_queryset(self):
        pet_pk = self.request.GET.get('pk')
        return Pet.objects.filter(pk=pet_pk).prefetch_related('vaccine_records', 'medication_records',
                                                              'examination_records')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = context['pet_list'][0]
        context['vaccines'] = pet.vaccine_records.all().order_by('-valid_until')
        context['treatments'] = pet.medication_records.all().order_by('-valid_until')
        context['examinations'] = pet.examination_records.all().order_by('-date_of_entry')
        context['id'] = pet.pk
        context['source'] = self.request.GET.get('source', '')
        return context


class ExaminationDetailsView(views.DetailView):
    model = MedicalExaminationRecord
    template_name = 'records/examination_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = context['object'].pet
        context['pet_pk'] = pet.pk
        return context


class BaseRecordAddView(views.CreateView, ABC):

    def get_pet(self):
        return get_object_or_404(Pet, pk=self.request.GET.get('pet_id'))

    def dispatch(self, request, *args, **kwargs):
        # Get the pet from the URL and assign it
        pet = self.get_pet()

        # Check if the owner is allowed to add vaccines
        if request.user in pet.owners.all() and not self.get_pet_attribute(pet):
            return HttpResponseForbidden("You can no longer add records for this pet.")

        # kwargs['pet_id'] = pet.pk
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pet = self.get_pet()
        context = super().get_context_data(**kwargs)
        context['pet_id'] = pet.pk
        return context

    def form_valid(self, form):
        form.instance.pet = self.get_pet()  # Assign the selected pet to the form
        return super().form_valid(form)

    @abstractmethod
    def get_pet_attribute(self, pet, value=None):
        pass

    @abstractmethod
    def get_success_url(self):
        pass


class VaccineRecordAddView(BaseRecordAddView):
    model = VaccinationRecord
    template_name = 'records/vaccine_record_add.html'
    form_class = VaccineRecordAddForm

    def get_success_url(self):
        pet = self.get_pet()
        base_url = reverse_lazy('vaccine-record-add')
        return f"{base_url}?pet_id={pet.pk}"

    def get_pet_attribute(self, pet, value=None):
        return pet.can_add_vaccines


class TreatmentRecordAddView(BaseRecordAddView):
    model = MedicationRecord
    template_name = 'records/treatment_record_add.html'
    form_class = TreatmentRecordAddForm

    def get_success_url(self):
        pet = self.get_pet()
        base_url = reverse_lazy('treatment-record-add')
        return f"{base_url}?pet_id={pet.pk}"

    def get_pet_attribute(self, pet, value=None):
        return pet.can_add_treatments


class BaseStopAddingRecordsView(views.View, ABC):

    def get(self, request, *args, **kwargs):
        pet = get_object_or_404(Pet, pk=self.request.GET.get('pet_id'))
        if request.user in pet.owners.all():
            self.set_pet_attribute(pet, False)
            pet.save()
        return redirect('pet-details', pk=pet.id)

    @abstractmethod
    def set_pet_attribute(self, pet, value):
        pass


class StopVaccineAdditionsView(BaseStopAddingRecordsView):

    def set_pet_attribute(self, pet, value):
        pet.can_add_vaccines = value


class StopTreatmentAdditionsView(BaseStopAddingRecordsView):

    def set_pet_attribute(self, pet, value):
        pet.can_add_treatments = value


class ExaminationAddView(views.FormView):
    template_name = 'records/examination_add.html'
    form_class = ExaminationForm
    success_url = reverse_lazy('pet_list')  # Change to appropriate URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.GET.get('pet_id'):
            kwargs['pet_id'] = self.request.GET.get('pet_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet_id = self.request.GET.get('pet_id')
        context['pet'] = get_object_or_404(Pet, pk=pet_id)

        # Initialize formsets
        VaccinationFormSet = formset_factory(VaccinationRecordForm, extra=1)
        MedicationFormSet = formset_factory(MedicationRecordForm, extra=1)

        if self.request.POST:
            context['vaccination_formset'] = VaccinationFormSet(self.request.POST, prefix='vaccinations')
            context['medication_formset'] = MedicationFormSet(self.request.POST, prefix='medications')
            context['blood_test_form'] = BloodTestForm(self.request.POST, prefix='blood_test')
            context['urine_test_form'] = UrineTestForm(self.request.POST, prefix='urine_test')
            context['fecal_test_form'] = FecalTestForm(self.request.POST, prefix='fecal_test')
        else:
            context['vaccination_formset'] = VaccinationFormSet(prefix='vaccinations')
            context['medication_formset'] = MedicationFormSet(prefix='medications')
            context['blood_test_form'] = BloodTestForm(prefix='blood_test')
            context['urine_test_form'] = UrineTestForm(prefix='urine_test')
            context['fecal_test_form'] = FecalTestForm(prefix='fecal_test')

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        vaccination_formset = context['vaccination_formset']
        medication_formset = context['medication_formset']
        blood_test_form = context['blood_test_form']
        urine_test_form = context['urine_test_form']
        fecal_test_form = context['fecal_test_form']

        pet_id = self.request.GET.get('pet_id')
        pet = get_object_or_404(Pet, pk=pet_id)

        # Check if all forms are valid
        if (vaccination_formset.is_valid() and medication_formset.is_valid() and
                (not form.cleaned_data.get('blood_test_needed') or blood_test_form.is_valid()) and
                (not form.cleaned_data.get('urine_test_needed') or urine_test_form.is_valid()) and
                (not form.cleaned_data.get('fecal_test_needed') or fecal_test_form.is_valid())):

            # Save the examination instance first without committing
            examination = form.save(commit=False)
            examination.pet = pet

            # Save related tests if needed
            if form.cleaned_data.get('blood_test_needed'):
                blood_test = blood_test_form.save()
                examination.blood_test = blood_test

            if form.cleaned_data.get('urine_test_needed'):
                urine_test = urine_test_form.save()
                examination.urine_test = urine_test

            if form.cleaned_data.get('fecal_test_needed'):
                fecal_test = fecal_test_form.save()
                examination.fecal_test = fecal_test

            # Save examination record
            examination.save()

            # Since the model has ForeignKey relationships for medication and vaccination,
            # we'll need to update the model to handle multiple records,
            # or modify this code to handle the current structure

            # For now, let's create the records separately:

            # Process and save vaccinations
            for vaccination_form in vaccination_formset:
                if vaccination_form.is_valid() and vaccination_form.has_changed():
                    vaccination = vaccination_form.save(commit=False)
                    vaccination.pet = pet
                    vaccination.save()
                    # You'll need to handle the relationship with examination
                    # This might need model changes to support many-to-many

            # Process and save medications
            for medication_form in medication_formset:
                if medication_form.is_valid() and medication_form.has_changed():
                    medication = medication_form.save(commit=False)
                    medication.pet = pet
                    medication.save()
                    # You'll need to handle the relationship with examination
                    # This might need model changes to support many-to-many

            messages.success(self.request, "Examination record created successfully!")
            # Redirect to the pet's detail page or somewhere appropriate
            return redirect('pet_detail', pk=pet_id)
        else:
            return self.form_invalid(form)
