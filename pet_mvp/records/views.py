from abc import ABC, abstractmethod
from django.contrib import messages
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic as views

from pet_mvp.drugs.models import BloodTest, UrineTest, FecalTest
from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import VaccinationRecordForm, MedicationRecordForm, FecalTestForm, UrineTestForm, \
    BloodTestForm, VaccinationRecordForm, MedicationRecordForm, VaccineFormSet, TreatmentFormSet, \
    MedicalExaminationRecordForm
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
        context['clinic'] = self.object.clinic.first()
        pet = context['object'].pet
        context['pet_pk'] = pet.pk
        context['source'] = self.request.GET.get('source')
        context['id'] = pet.id
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
    form_class = VaccinationRecordForm

    def get_success_url(self):
        pet = self.get_pet()
        base_url = reverse_lazy('vaccine-record-add')
        return f"{base_url}?pet_id={pet.pk}"

    def get_pet_attribute(self, pet, value=None):
        return pet.can_add_vaccines


class TreatmentRecordAddView(BaseRecordAddView):
    model = MedicationRecord
    template_name = 'records/treatment_record_add.html'
    form_class = MedicationRecordForm

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


class MedicalExaminationReportCreateView(views.FormView):
    template_name = 'records/examination_add.html'
    form_class = MedicalExaminationRecordForm

    # def get_initial(self):
    #     code = self.request.GET.get('code')
    #     pet = get_object_or_404(Pet, pet_access_code__code=code)
    #     clinic = self.request.user
    #     return {'pet': pet, 'clinic': clinic}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        code = self.request.GET.get('code')
        # TODO add pet and clinic to the vaccine report and medicine report
        pet = get_object_or_404(Pet, pet_access_code__code=code)
        clinic = self.request.user

        context['pet'] = pet
        context['code'] = code
        context['source'] = self.request.GET.get('source')

        post_data = self.request.POST or None

        context['report_form'] = MedicalExaminationRecordForm(post_data)
        context['vaccine_formset'] = VaccineFormSet(post_data, prefix='vaccines',
                                                    queryset=VaccinationRecord.objects.none())
        context['treatment_formset'] = TreatmentFormSet(post_data, prefix='treatments',
                                                        queryset=MedicationRecord.objects.none())
        context['blood_test_form'] = BloodTestForm(post_data)
        context['urine_test_form'] = UrineTestForm(post_data)
        context['fecal_test_form'] = FecalTestForm(post_data)

        context['additional_info_fields'] = [
            'general_health', 'body_condition_score', 'temperature',
            'heart_rate', 'respiratory_rate', 'mucous_membrane_color',
            'hydration_status', 'skin_and_coat_condition',
            'teeth_and_gums', 'eyes_ears_nose', 'diagnosis',
        ]

        return context

    def form_valid(self, form):


        vaccine_formset = VaccineFormSet(self.request.POST, prefix='vaccines')
        treatment_formset = TreatmentFormSet(self.request.POST, prefix='treatments')
        blood_test_form = BloodTestForm(self.request.POST)
        urine_test_form = UrineTestForm(self.request.POST)
        fecal_test_form = FecalTestForm(self.request.POST)

        with transaction.atomic():
            if vaccine_formset.is_valid() and \
                    treatment_formset.is_valid() and \
                    blood_test_form.is_valid() and \
                    urine_test_form.is_valid() and \
                    fecal_test_form.is_valid():

                vaccines = vaccine_formset.save()
                treatments = treatment_formset.save()
                blood_test = blood_test_form.save()
                urine_test = urine_test_form.save()
                fecal_test = fecal_test_form.save()


                form.instance.blood_test = blood_test
                form.instance.urine_test = urine_test
                form.instance.fecal_test = fecal_test

                form.save()
                form.instance.pet = get_object_or_404(Pet, pet_access_code__code=form.cleaned_data['code'])
                form.instance.clinic.set(self.request.user)
                form.instance.vaccines.set(vaccines)
                form.instance.treatments.set(treatments)

                messages.success(self.request, "Examination data saved successfully!")
                return redirect(reverse_lazy('clinic-dashboard') + f'?code={form.cleaned_data["code"]}')
            else:
                return self.form_invalid(form)
