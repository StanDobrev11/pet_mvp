from django.urls import path, include

from pet_mvp.drugs.views import VaccineDetailsView, DrugDetailsView, BloodTestDetailsView, UrineTestDetailsView, \
    FecalTestDetailsView

urlpatterns = [
    path('vaccines/', include([
        path('<int:pk>/', VaccineDetailsView.as_view(), name='vaccine-details')
    ])),
    path('treatments/', include([
        path('<int:pk>/', DrugDetailsView.as_view(), name='treatment-details')
    ])),
    path('tests/', include([
        path('blood-tests/', include(
            [
                path('<int:pk>/', include([
                    path('details/', BloodTestDetailsView.as_view(), name='blood-test-details')
                ]))
            ]
        )),
        path('urine-tests/', include([
            path('<int:pk>/', include([
                path('details/', UrineTestDetailsView.as_view(), name='urine-test-details')
            ]))
        ])),
        path('fecal-tests/', include([
            path('<int:pk>/', include([
                path('details/', FecalTestDetailsView.as_view(), name='fecal-test-details')
            ]))
        ]))
    ]))
]
