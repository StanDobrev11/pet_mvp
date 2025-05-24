from django.contrib.auth.decorators import login_not_required
from django.urls import path, include

from pet_mvp.common.views import AboutView, IndexView, DashboardView

urlpatterns = [
    path('', login_not_required(IndexView.as_view()), name='index'),
    path('about/', login_not_required(AboutView.as_view()), name='about'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
