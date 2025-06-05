from django.contrib.auth.decorators import login_not_required
from django.urls import path

from pet_mvp.common.views import AboutView, IndexView, DashboardView, ClinicDashboardView, robots_txt

urlpatterns = [
    path('', login_not_required(IndexView.as_view()), name='index'),
    path('about/', login_not_required(AboutView.as_view()), name='about'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('clinic-dashboard/', ClinicDashboardView.as_view(), name='clinic-dashboard'),
    path("robots.txt", login_not_required(robots_txt), name="robots_txt"),
]
