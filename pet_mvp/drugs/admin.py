from django.contrib import admin

from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ('name', 'core', 'suitable_for', 'notes')
    list_filter = ('core', 'suitable_for')
    search_fields = ('name', 'notes')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'core')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
    )


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'suitable_for', 'notes')
    search_fields = ('name', 'notes')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name',)
        }),
        ('Details', {
            'fields': ('notes',)
        }),
    )


@admin.register(BloodTest)
class BloodTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_conducted', 'white_blood_cells', 'red_blood_cells', 'hemoglobin', 'platelets')
    list_filter = ('date_conducted',)
    search_fields = ('result', 'additional_notes')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        ('Basic Information', {
            'fields': ('date_conducted', 'result')
        }),
        ('Blood Cell Counts', {
            'fields': ('white_blood_cells', 'red_blood_cells', 'hemoglobin', 'platelets')
        }),
        ('Additional Information', {
            'fields': ('additional_notes',)
        }),
    )


@admin.register(UrineTest)
class UrineTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_conducted', 'color', 'clarity', 'ph', 'specific_gravity')
    list_filter = ('date_conducted', 'color', 'clarity')
    search_fields = ('result', 'additional_notes', 'color', 'clarity')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        ('Basic Information', {
            'fields': ('date_conducted', 'result')
        }),
        ('Physical Properties', {
            'fields': ('color', 'clarity', 'ph', 'specific_gravity')
        }),
        ('Chemical Analysis', {
            'fields': ('protein', 'glucose', 'red_blood_cells', 'white_blood_cells')
        }),
        ('Additional Information', {
            'fields': ('additional_notes',)
        }),
    )


@admin.register(FecalTest)
class FecalTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_conducted', 'consistency')
    list_filter = ('date_conducted', 'consistency')
    search_fields = ('result', 'additional_notes', 'consistency')
    date_hierarchy = 'date_conducted'
    fieldsets = (
        ('Basic Information', {
            'fields': ('date_conducted', 'result')
        }),
        ('Physical Properties', {
            'fields': ('consistency',)
        }),
        ('Additional Information', {
            'fields': ('additional_notes',)
        }),
    )
