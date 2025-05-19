from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django.shortcuts import redirect, get_object_or_404

from django.views import generic as views

from pet_mvp.pets.models import Pet

UserModel = get_user_model()


class IndexView(views.TemplateView):
    template_name = 'common/index.html'
    login_required = False

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            if not request.user.is_owner:
                code = request.session.get('code')
                pet_id = get_object_or_404(Pet, pet_access_code__code=code).pk
                return redirect('pet-details', pk=pet_id)

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
