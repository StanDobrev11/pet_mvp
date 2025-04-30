from django.urls import path

from pet_mvp.records.views import RecordListView

urlpatterns = [
    path('', RecordListView.as_view(), name='record-list')
]