from django.shortcuts import render

from django.views import generic as views

from pet_mvp.records.models import VaccinationRecord, MedicationRecord


# Create your views here.
class VaccineDetailsView(views.DetailView):
    model = VaccinationRecord
    template_name = "drugs/vaccine-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = context['object'].pet
        context['pet_pk'] = pet.pk
        return context


class DrugDetailsView(views.DetailView):
    model = MedicationRecord
    template_name = "drugs/treatment-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = context['object'].pet
        context['pet_pk'] = pet.pk
        return context


