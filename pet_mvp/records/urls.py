from django.urls import path, include

from pet_mvp.records.views import RecordListView, ExaminationDetailsView, VaccineRecordAddView, StopVaccineAdditionsView, TreatmentRecordAddView, StopTreatmentAdditionsView

urlpatterns = [
    path('', RecordListView.as_view(), name='record-list'),
    path('vaccine-records/', include([
        path('add/', VaccineRecordAddView.as_view(), name='vaccine-record-add'),
        path('stop/', StopVaccineAdditionsView.as_view(), name='vaccine-record-stop'),
    ])),
    path('treatment-records/', include([
        path('add/', TreatmentRecordAddView.as_view(), name='treatment-record-add'),
        path('stop/', StopTreatmentAdditionsView.as_view(), name='treatment-record-stop'),
    ])),
    path('examinations/', include([
        path('<int:pk>/', ExaminationDetailsView.as_view(), name='exam-details')
    ]))
]