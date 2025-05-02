from django.shortcuts import render
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

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     pet_pk = self.request.GET.get('pk')