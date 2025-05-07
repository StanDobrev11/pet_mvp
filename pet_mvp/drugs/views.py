from abc import ABC

from django.shortcuts import render

from django.views import generic as views

from pet_mvp.drugs.models import BloodTest, UrineTest, FecalTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord


# Create your views here.
class BaseDetailsView(views.DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = self.request.GET.get('source', '')
        context['id'] = self.request.GET.get('id', '')
        return context


class VaccineDetailsView(BaseDetailsView):
    model = VaccinationRecord
    template_name = "drugs/vaccine-details.html"


class DrugDetailsView(BaseDetailsView):
    model = MedicationRecord
    template_name = "drugs/treatment-details.html"


class BloodTestDetailsView(BaseDetailsView):
    model = BloodTest
    template_name = "drugs/blood_test_details.html"


class UrineTestDetailsView(BaseDetailsView):
    model = UrineTest
    template_name = "drugs/urine_test_details.html"


class FecalTestDetailsView(BaseDetailsView):
    model = FecalTest
    template_name = "drugs/fecal_test_details.html"