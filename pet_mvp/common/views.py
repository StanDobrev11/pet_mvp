from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic as views


UserModel = get_user_model()


class IndexView(views.TemplateView):
    template_name = 'common/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

