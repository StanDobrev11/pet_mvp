from abc import ABC, abstractmethod

from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic as views

from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import VaccineRecordAddForm, TreatmentRecordAddForm
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
        context['pet_pk'] = pet.pk
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
