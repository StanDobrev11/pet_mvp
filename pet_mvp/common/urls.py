from django.urls import path, include

from pet_mvp.common.views import IndexView, DashboardView, ClinicDashboard

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('clinic-dashboard/', ClinicDashboard.as_view(), name='clinic-dashboard'),
]
