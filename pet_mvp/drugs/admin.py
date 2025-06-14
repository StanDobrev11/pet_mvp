from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ('name', 'core', 'suitable_for', 'recommended_interval_days', 'notes')
    list_filter = ('core', 'suitable_for')
    search_fields = ('name', 'notes')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'core', 'suitable_for')
        }),
        (_('Scheduling'), {
            'fields': ('recommended_interval_days',)
        }),
        (_('Details'), {
            'fields': ('notes',)
        }),
    )


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'suitable_for', 'is_antiparasite', 'recommended_interval_days', 'notes')
    list_filter = ('suitable_for',)
    search_fields = ('name', 'notes')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'suitable_for', 'is_antiparasite')
        }),
        (_('Scheduling'), {
            'fields': ('recommended_interval_days',)
        }),
        (_('Details'), {
            'fields': ('notes',)
        }),
    )


@admin.register(BloodTest)
class BloodTestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date_conducted', 'white_blood_cells', 'red_blood_cells', 'hemoglobin', 'platelets'
    )
    list_filter = ('date_conducted',)
    search_fields = ('result', 'additional_notes')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('date_conducted', 'result')
        }),
        (_('Blood Cell Counts'), {
            'fields': ('white_blood_cells', 'red_blood_cells', 'hemoglobin', 'platelets')
        }),
        (_('Additional Information'), {
            'fields': ('additional_notes',)
        }),
    )


@admin.register(UrineTest)
class UrineTestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date_conducted', 'color', 'clarity', 'ph', 'specific_gravity'
    )
    list_filter = ('date_conducted', 'color', 'clarity')
    search_fields = ('result', 'additional_notes', 'color', 'clarity')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('date_conducted', 'result')
        }),
        (_('Physical Properties'), {
            'fields': ('color', 'clarity', 'ph', 'specific_gravity')
        }),
        (_('Chemical Analysis'), {
            'fields': ('protein', 'glucose', 'red_blood_cells', 'white_blood_cells')
        }),
        (_('Additional Information'), {
            'fields': ('additional_notes',)
        }),
    )


@admin.register(FecalTest)
class FecalTestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date_conducted', 'consistency', 'parasites_detected', 'blood_presence'
    )
    list_filter = ('date_conducted', 'consistency', 'parasites_detected', 'blood_presence')
    search_fields = ('result', 'additional_notes', 'consistency', 'parasite_type')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('date_conducted', 'result')
        }),
        (_('Physical Properties'), {
            'fields': ('consistency',)
        }),
        (_('Findings'), {
            'fields': ('parasites_detected', 'parasite_type', 'blood_presence')
        }),
        (_('Additional Information'), {
            'fields': ('additional_notes',)
        }),
    )
