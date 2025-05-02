from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic as views

from pet_mvp.pets.models import Pet
from pet_mvp.records.forms import VaccineRecordAddForm
from pet_mvp.records.models import VaccinationRecord, MedicalExaminationRecord


# Create your views here.
class RecordListView(views.ListView):
    template_name = 'records/record_list.html'

    def get_queryset(self):
        pet_pk = self.request.GET.get('pk')
        return Pet.objects.filter(pk=pet_pk).prefetch_related('vaccine_records', 'medication_records', 'examination_records')

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


class VaccineRecordAddView(views.CreateView):
    model = VaccinationRecord
    template_name = 'records/vaccine_record_add.html'
    form_class = VaccineRecordAddForm

    def dispatch(self, request, *args, **kwargs):
        # Get the pet from the URL and assign it
        self.pet = get_object_or_404(Pet, pk=self.request.GET.get('pet_id'))

        # Check if the owner is allowed to add vaccines
        if request.user in self.pet.owners.all() and not self.pet.can_add_vaccines:
            return HttpResponseForbidden("You can no longer add vaccination records for this pet.")

        kwargs['pet_id'] = self.pet.pk
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet_id'] = self.pet.pk
        return context

    def form_valid(self, form):
        form.instance.pet = self.pet  # Assign the selected pet to the form
        return super().form_valid(form)

    def get_success_url(self):
        base_url = reverse_lazy('vaccine-record-add')
        return f"{base_url}?pet_id={self.pet.pk}"


class StopVaccineAdditionsView(views.View):
    def post(self, request, *args, **kwargs):
        pet = get_object_or_404(Pet, pk=self.request.GET.get('pet_id'))
        if request.user in pet.owners.all():
            pet.can_add_vaccines = False
            pet.save()
        return redirect('pet-details', pk=pet.id)
