import os
import random

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import generic as views
from django.utils import timezone
from django.http import HttpResponse

from pet_mvp.common.models import Testimonial
from pet_mvp.pets.models import Pet
from pet_mvp.settings import GOOGLE_MAPS_API_KEY

UserModel = get_user_model()


class AboutView(views.TemplateView):
    template_name = 'common/about.html'


class IndexView(views.TemplateView):
    template_name = 'common/index.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            if not request.user.is_owner:
                code = request.session.get('code')
                try:
                    pet = Pet.objects.get(pet_access_code__code=code)
                except Pet.DoesNotExist:
                    return redirect('clinic-dashboard')
                return redirect('pet-details', pk=pet.id)

            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_testimonials = Testimonial.objects.filter(is_active=True)
        total = active_testimonials.count()
        count = min(total, 6)

        context["testimonials"] = random.sample(list(active_testimonials), count)
        context['pet_image_numbers'] = range(1, 7)  # generates 1 through 6

        return context


class DashboardView(views.TemplateView):
    template_name = 'common/dashboard.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_owner:
            messages.error(self.request, _('You do not have permission to access this page.'))
            return redirect('clinic-dashboard')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY')

        user = self.request.user
        pets = user.pets.all()
        context['pets'] = pets

        return context


class ClinicDashboardView(views.TemplateView):
    template_name = 'accounts/../../templates/common/clinic_dashboard.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_owner:
            messages.error(self.request, _('You do not have permission to access this page.'))
            return redirect('clinic-dashboard')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vet = self.request.user

        # Only include currently valid pet access
        accessible_pets = Pet.objects.filter(
            vetpetaccess__vet=vet,
            vetpetaccess__expires_at__gt=timezone.now()
        ).distinct()

        context['accessible_pets'] = accessible_pets
        return context

def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow:",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")