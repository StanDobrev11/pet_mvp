from django.urls import path, include

from pet_mvp.records.views import RecordListView, ExaminationDetailsView, VaccineRecordAddView, \
    StopVaccineAdditionsView, TreatmentRecordAddView, MedicalExaminationReportCreateView, VaccineRecordEditView, \
    TreatmentRecordEditView, VaccineWrongReportView, VaccineResetView

urlpatterns = [
    path('', RecordListView.as_view(), name='record-list'),
    path('vaccine-records/', include([
        path('<int:pk>/', include([
            path('edit/', VaccineRecordEditView.as_view(), name='vaccine-record-edit'),
            path('report/', VaccineWrongReportView.as_view(), name='vaccine-record-report'),
        ])),
        path('<uidb64>/<token>/reset/', VaccineResetView.as_view(), name='vaccine-record-reset'),
        path('add/', VaccineRecordAddView.as_view(), name='vaccine-record-add'),
        path('stop/', StopVaccineAdditionsView.as_view(),
             name='vaccine-record-stop'),
    ])),
    path('treatment-records/', include([
        path('<int:pk>/edit/', TreatmentRecordEditView.as_view(), name='treatment-record-edit'),
        path('add/', TreatmentRecordAddView.as_view(),
             name='treatment-record-add'),
    ])),
    path('examinations/', include([
        path('<int:pk>/', ExaminationDetailsView.as_view(), name='exam-details'),
        path('add/', MedicalExaminationReportCreateView.as_view(), name='exam-add'),
    ])),
]
