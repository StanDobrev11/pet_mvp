from django.shortcuts import render

from django.views import generic as views

from pet_mvp.records.models import VaccinationRecord


# Create your views here.
class VaccineDetailsView(views.DetailView):
    model = VaccinationRecord
    template_name = "drugs/vaccine-details.html"
