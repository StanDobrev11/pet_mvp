from django.urls import path, include

from pet_mvp.common.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
