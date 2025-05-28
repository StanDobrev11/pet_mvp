from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import generic as views
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.contrib import messages

from pet_mvp.access_codes.utils import generate_access_code
from pet_mvp.notifications.tasks import send_owner_pet_addition_request
from pet_mvp.pets.forms import AddExistingPetForm, PetAddForm, MarkingAddForm, PetEditForm
from pet_mvp.pets.models import Pet

UserModel = get_user_model()
signer = Signer()

# Create your views here.


class PetDetailView(views.DetailView):
    model = Pet
    template_name = "pet/pet_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the pet
        pet = Pet.objects.get(pk=self.kwargs['pk'])

        # generate code
        user = self.request.user
        if user.is_owner:
            access_code = generate_access_code(pet)
            context['access_code'] = access_code.code

        context['valid_vaccinations'] = pet.vaccine_records.filter(valid_until__gte=date.today()).order_by(
            '-valid_until')
        context['valid_treatments'] = pet.medication_records.filter(valid_until__gte=date.today()).order_by(
            '-created_at')
        context['last_examinations'] = pet.examination_records.all().order_by(
            '-created_at')[:3]

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dog_breeds'] = Pet.DOG_BREED_CHOICES
        context['cat_breeds'] = Pet.CAT_BREED_CHOICES
        return context

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_valid(self, form):
        new_pet = form.save()
        new_pet.owners.add(self.request.user)

        return redirect('dashboard')


class AddExistingPetView(views.FormView):
    form_class = AddExistingPetForm
    template_name = 'pet/pet_add_existing.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        passport_number = form.cleaned_data['passport_number']

        try:
            pet = Pet.objects.get(passport_number=passport_number)
        except Pet.DoesNotExist:
            form.add_error('passport_number', _('Invalid passport number: no pet found with these details.'))
            return self.form_invalid(form)

        existing_owner = pet.owners.first()
        token = signer.sign(f'{pet.id}:{self.request.user.id}')
        approval_url = self.request.build_absolute_uri(
            reverse('approve-pet-addition', args=[token])
        )

        send_owner_pet_addition_request(
            existing_owner=existing_owner,
            new_owner=self.request.user,
            pet=pet,
            approval_url=approval_url
        )

        messages.success(self.request, _(
            "Your request to access the pet has been sent to the owner."))

        return redirect(self.get_success_url())


class ApprovePetAdditionView(views.View):
    def get(self, request, token):
        try:
            data = signer.unsign(token)
            pet_id, user_id = map(int, data.split(':')) 
            pet = Pet.objects.get(id=pet_id)
            user = UserModel.objects.get(id=user_id)

            pet.owners.add(user)
            # pet.pending_owners.remove(user)

            context = {
                "pet_name": pet.name,
                "new_owner": user.get_full_name(),
            }
            return render(request, "pet/approve_confirmation.html", context)

        except (BadSignature, Pet.DoesNotExist, UserModel.DoesNotExist):
            return HttpResponseBadRequest(_('Invalid or expired link.'))


class PetDeleteView(views.DeleteView):
    model = Pet
    success_url = reverse_lazy('dashboard')
    template_name = 'pet/pet_delete.html'

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
    template_name = 'pet/marking_details.html'

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
