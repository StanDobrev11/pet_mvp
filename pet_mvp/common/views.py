# Create your views here.
import code

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
    template_name = 'common/clinic_dashboard.html'

    def get_object(self, queryset=None):
        code = self.request.GET.get('code')
        pet = Pet.objects.get(pet_access_code__code=code)

        return pet
