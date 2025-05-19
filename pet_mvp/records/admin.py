from django.contrib import admin

from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

# Register models
@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ('vaccine', 'pet', 'date_of_vaccination', 'valid_until', 'batch_number', 'manufacturer')
    list_filter = ('vaccine', 'pet', 'date_of_vaccination')
    search_fields = ('vaccine__name', 'pet__name', 'batch_number', 'manufacturer')
    date_hierarchy = 'date_of_vaccination'


@admin.register(MedicationRecord)
class MedicationRecordAdmin(admin.ModelAdmin):
    list_display = ('medication', 'pet', 'date', 'dosage', 'valid_until', 'manufacturer')
    list_filter = ('medication', 'pet', 'date')
    search_fields = ('medication__name', 'pet__name', 'dosage', 'manufacturer')
    date_hierarchy = 'date'


@admin.register(MedicalExaminationRecord)
class MedicalExaminationRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'exam_type', 'date_of_entry', 'doctor', 'clinic', 'reason_for_visit')
    list_filter = ('exam_type', 'pet', 'clinic', 'date_of_entry')
    search_fields = ('pet__name', 'doctor', 'reason_for_visit', 'general_health')
    date_hierarchy = 'date_of_entry'
    fieldsets = (
        ('Basic Information', {
            'fields': ('pet', 'exam_type', 'date_of_entry', 'doctor', 'clinic', 'reason_for_visit')
        }),
        ('Health Assessment', {
            'fields': ('general_health', 'body_condition_score', 'temperature', 'heart_rate', 'respiratory_rate')
        }),
    )
