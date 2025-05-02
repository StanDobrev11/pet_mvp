from django.urls import path, include

from pet_mvp.records.views import RecordListView, ExaminationDetailsView, VaccineRecordAddView

urlpatterns = [
    path('', RecordListView.as_view(), name='record-list'),
    path('vaccine-records/', include([
        path('add/', VaccineRecordAddView.as_view(), name='vaccine-record-add')
    ])),

    path('examinations/', include([
        path('<int:pk>/', ExaminationDetailsView.as_view(), name='exam-details')
    ]))
]
