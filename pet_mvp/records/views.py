from abc import ABC, abstractmethod
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic as views
from django.utils.translation import gettext_lazy as _


from pet_mvp.notifications.tasks import send_medical_record_email
from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import FecalTestForm, UrineTestForm, \
    BloodTestForm, VaccinationRecordForm, MedicationRecordForm, VaccineFormSet, TreatmentFormSet, \
    MedicalExaminationRecordForm
from pet_mvp.records.models import VaccinationRecord, MedicalExaminationRecord, MedicationRecord


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
        context['treatments'] = pet.medication_records.all().order_by(
            '-valid_until')
        context['examinations'] = pet.examination_records.all().order_by(
            '-date_of_entry')
        context['id'] = pet.pk
        context['source'] = self.request.GET.get('source', '')
        return context


class BaseRecordAddView(views.CreateView, ABC):

    def get_pet(self):
        return get_object_or_404(Pet, pk=self.request.GET.get('pet_id'))

    def get_context_data(self, **kwargs):
        pet = self.get_pet()
        context = super().get_context_data(**kwargs)
        context['pet_id'] = pet.pk
        return context

    def form_valid(self, form):
        form.instance.pet = self.get_pet()
        messages.success(self.request, _(
            "Record saved. You can now add another."))
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pet'] = self.get_pet()
        return kwargs


class VaccineRecordAddView(BaseRecordAddView):
    model = VaccinationRecord
    template_name = 'records/vaccine_record_add.html'
    form_class = VaccinationRecordForm

    def dispatch(self, request, *args, **kwargs):
        pet = self.get_pet()
        if request.user in pet.owners.all() and not self.get_pet_attribute(pet):
            return HttpResponseForbidden(_("You can no longer add records for this pet."))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pet = self.get_pet()
        base_url = reverse_lazy('vaccine-record-add')
        return f"{base_url}?pet_id={pet.pk}"

    def get_pet_attribute(self, pet, value=None):
        return pet.can_add_vaccines


class TreatmentRecordAddView(BaseRecordAddView):
    """ This view will be used to add directly by the owner treatments and medications """
    model = MedicationRecord
    template_name = 'records/treatment_record_add.html'
    form_class = MedicationRecordForm

    def get_success_url(self):
        pet = self.get_pet()
        base_url = reverse('treatment-record-add')
        return f"{base_url}?pet_id={pet.pk}"


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


class ExaminationDetailsView(views.DetailView):
    model = MedicalExaminationRecord
    template_name = 'records/examination_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = context['object'].pet
        context['clinic'] = self.object.clinic
        context['pet_pk'] = pet.pk
        context['source'] = self.request.GET.get('source')
        context['id'] = pet.id
        return context


class MedicalExaminationReportCreateView(views.FormView):
    template_name = 'records/examination_add.html'
    form_class = MedicalExaminationRecordForm

    def get_pet(self, pet_id=None, ):
        if pet_id:
            return get_object_or_404(Pet, pk=pet_id)

        pet_id = self.request.GET.get('id')

        if pet_id is None:
            pet_id = self.request.POST.get('id')
        return get_object_or_404(Pet, pk=pet_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pet = self.get_pet()

        context['pet'] = pet
        context['id'] = pet.pk
        context['source'] = self.request.GET.get('source')

        post_data = self.request.POST or None

        context['report_form'] = MedicalExaminationRecordForm(post_data)
        context['vaccine_formset'] = VaccineFormSet(post_data, prefix='vaccines',
                                                    queryset=VaccinationRecord.objects.none(),
                                                    pet=pet)
        context['treatment_formset'] = TreatmentFormSet(data=post_data, prefix='treatments',
                                                        queryset=MedicationRecord.objects.none(),
                                                        pet=pet)
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


    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.error(self.request, _("Please correct the errors in the form."))
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        pet = self.get_pet()

        vaccine_formset = VaccineFormSet(self.request.POST, prefix='vaccines', pet=pet)
        treatment_formset = TreatmentFormSet(self.request.POST, prefix='treatments', pet=pet)
        request_data = self.request.POST

        # Check if main form and all formsets are valid
        all_valid = True

        if not vaccine_formset.is_valid():
            messages.error(
                self.request, _("Vaccine information contains errors."))
            all_valid = False

        if not treatment_formset.is_valid():
            messages.error(
                self.request, _("Treatment information contains errors."))
            all_valid = False

        # Check optional test forms if they're included
        if request_data.get('has_blood_test'):
            blood_test_form = BloodTestForm(request_data)
            if not blood_test_form.is_valid():
                messages.error(
                    self.request, _("Blood test form contains errors."))
                all_valid = False

        if request_data.get('has_urine_test'):
            urine_test_form = UrineTestForm(request_data)
            if not urine_test_form.is_valid():
                messages.error(
                    self.request, _("Urine test form contains errors."))
                all_valid = False

        if request_data.get('has_fecal_test'):
            fecal_test_form = FecalTestForm(request_data)
            if not fecal_test_form.is_valid():
                messages.error(
                    self.request, _("Fecal test form contains errors."))
                all_valid = False

        # If any form is invalid, return to the same page with form data preserved
        if not all_valid:
            return self.form_invalid(form)

        # If all forms are valid, proceed with saving
        with transaction.atomic():
            # Set foreign keys early
            form.instance.pet = pet
            form.instance.clinic = self.request.user
            report = form.save()

            # Vaccines
            vaccines = vaccine_formset.save(commit=False)
            for vaccine in vaccines:
                vaccine.pet = pet
                if vaccine.vaccine.name in ['Rabies', ]:
                    vaccine.valid_from += timedelta(days=7)
                vaccine.save()
            report.vaccinations.set(vaccines)

            # Treatments
            treatments = treatment_formset.save(commit=False)
            for treatment in treatments:
                treatment.pet = pet
                treatment.save()
            report.medications.set(treatments)

            # Optional test forms
            if request_data.get('has_blood_test'):
                blood_test_form = BloodTestForm(request_data)
                report.blood_test = blood_test_form.save()

            if request_data.get('has_urine_test'):
                urine_test_form = UrineTestForm(request_data)
                report.urine_test = urine_test_form.save()

            if request_data.get('has_fecal_test'):
                fecal_test_form = FecalTestForm(request_data)
                report.fecal_test = fecal_test_form.save()

            report.save()

        lang = self.request.COOKIES.get('django_language', 'en')
        send_medical_record_email(report, lang)
        messages.success(self.request, _("Examination data saved successfully!"))
        return redirect(reverse_lazy('pet-details', kwargs={'pk': pet.pk}))
