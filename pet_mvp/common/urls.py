from django.urls import path, include

from pet_mvp.common.views import IndexView, DashboardView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
