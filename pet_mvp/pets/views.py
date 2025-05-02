from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic as views

from pet_mvp.pets.forms import PetAddForm, MarkingAddForm, PetEditForm
from pet_mvp.pets.models import Pet


# Create your views here.
class PetDetailView(views.DetailView):
    model = Pet
    template_name = "pet/pet_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = Pet.objects.get(pk=self.kwargs['pk'])
        context['valid_vaccinations'] = pet.vaccine_records.filter(valid_until__gte=date.today())
        context['valid_treatments'] = pet.medication_records.filter(valid_until__gte=date.today())
        context['last_examinations'] = pet.examination_records.all()[:3]
        return context


class PetEditView(views.UpdateView):
    model = Pet
    template_name = "pet/pet_edit.html"
    form_class = PetEditForm

    def get_success_url(self):
        return reverse_lazy('pet-details', kwargs={'pk': self.object.pk})


class PetAddView(views.CreateView):
    model = Pet
    template_name = "pet/pet_add.html"
    form_class = PetAddForm

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_valid(self, form):
        new_pet = form.save()
        new_pet.owners.add(self.request.user)

        return redirect('dashboard')


class PetDeleteView(views.DeleteView):
    model = Pet
    success_url = reverse_lazy('dashboard')
    template_name = 'pet/pet-delete.html'

    def get_object(self, queryset=None):
        return Pet.objects.get(pk=self.kwargs['pk'])


class MarkingAddView(views.FormView):
    template_name = 'pet/marking_add.html'
    form_class = MarkingAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet'] = get_object_or_404(Pet, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        pet = get_object_or_404(Pet, pk=self.kwargs['pk'])
        self.object = form.save(pet=pet)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('pet-details', kwargs={'pk': self.kwargs['pk']})


class MarkingDetailsView(views.DetailView):
    template_name = 'pet/marking-details.html'

    def get_queryset(self):
        return Pet.objects.filter(pk=self.kwargs['pk'])

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pet = queryset.first()

        try:
            return pet.transponder
        except ObjectDoesNotExist:
            pass

        try:
            return pet.tattoo
        except ObjectDoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet_pk'] = self.kwargs['pk']

        return context
