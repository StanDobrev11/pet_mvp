from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pet_mvp.records.models import (
    VaccinationRecord,
    MedicationRecord,
    MedicalExaminationRecord,
)


@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ('vaccine', 'pet', 'date_of_vaccination', 'valid_until', 'batch_number', 'manufacturer')
    list_filter = ('vaccine', 'pet', 'date_of_vaccination')
    search_fields = ('vaccine__name', 'pet__name', 'batch_number', 'manufacturer')
    date_hierarchy = 'date_of_vaccination'
    fieldsets = (
        (_('Vaccination Details'), {
            'fields': ('vaccine', 'pet', 'date_of_vaccination', 'valid_from', 'valid_until')
        }),
        (_('Manufacturing Info'), {
            'fields': ('manufacturer', 'manufacture_date', 'batch_number')
        }),
    )


@admin.register(MedicationRecord)
class MedicationRecordAdmin(admin.ModelAdmin):
    list_display = ('medication', 'pet', 'date', 'dosage', 'valid_until', 'manufacturer')
    list_filter = ('medication', 'pet', 'date')
    search_fields = ('medication__name', 'pet__name', 'dosage', 'manufacturer')
    date_hierarchy = 'date'
    fieldsets = (
        (_('Medication Details'), {
            'fields': ('medication', 'pet', 'date', 'time', 'dosage', 'valid_until')
        }),
        (_('Manufacturer Info'), {
            'fields': ('manufacturer',)
        }),
    )


@admin.register(MedicalExaminationRecord)
class MedicalExaminationRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'exam_type', 'date_of_entry', 'doctor', 'clinic', 'reason_for_visit')
    list_filter = ('exam_type', 'pet', 'clinic', 'date_of_entry')
    search_fields = ('pet__name', 'doctor', 'reason_for_visit', 'general_health')
    date_hierarchy = 'date_of_entry'

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('pet', 'exam_type', 'date_of_entry', 'doctor', 'clinic', 'reason_for_visit')
        }),
        (_('Health Assessment'), {
            'fields': (
                'general_health', 'body_condition_score', 'temperature', 'heart_rate', 'respiratory_rate',
                'mucous_membrane_color', 'hydration_status'
            )
        }),
        (_('Physical Condition'), {
            'fields': (
                'skin_and_coat_condition', 'teeth_and_gums', 'eyes_ears_nose'
            )
        }),
        (_('Lab Tests'), {
            'fields': ('blood_test', 'urine_test', 'fecal_test')
        }),
        (_('Treatments & Diagnosis'), {
            'fields': ('treatment_performed', 'diagnosis', 'follow_up')
        }),
        (_('Prescribed Records'), {
            'fields': ('medications', 'vaccinations')
        }),
        (_('Additional Notes'), {
            'fields': ('notes',)
        }),
    )
