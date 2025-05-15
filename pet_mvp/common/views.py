# Create your views here.
import code
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django.shortcuts import redirect

from django.views import generic as views

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class IndexView(views.TemplateView):
    template_name = 'common/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class DashboardView(auth_mixins.LoginRequiredMixin, views.TemplateView):
    template_name = 'common/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if user.is_authenticated:
            pets = user.pets.all()
            context['pets'] = pets

        return context


class ClinicDashboard(auth_mixins.LoginRequiredMixin, views.DetailView):
    template_name = 'pet/pet_details.html'

    def get_object(self, queryset=None):
        code = self.request.GET.get('code')
        pet = Pet.objects.get(pet_access_code__code=code)

        return pet

    def get_context_data(self, **kwargs):
        pass
        # pet = self.get_object()
        #
        # context = super().get_context_data(**kwargs)
        # context['valid_vaccinations'] = pet.vaccine_records.filter(valid_until__gte=date.today()).order_by('-valid_until')
        # context['valid_treatments'] = pet.medication_records.filter(valid_until__gte=date.today()).order_by('-created_at')
        # context['last_examinations'] = pet.examination_records.all().order_by('-created_at')[:3]
        # context['code'] = self.request.GET.get('code')
        # return context
