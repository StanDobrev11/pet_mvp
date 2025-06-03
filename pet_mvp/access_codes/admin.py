from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pet_mvp.access_codes.models import PetAccessCode, QRShareToken, VetPetAccess


@admin.register(PetAccessCode)
class PetAccessCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('code', 'pet__name')
    readonly_fields = ('is_valid',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Access Code'), {
            'fields': ('code', 'pet')
        }),
        (_('Validity'), {
            'fields': ('expires_at', 'is_valid')
        }),
    )

    def is_valid(self, obj):
        return obj.is_valid

    is_valid.boolean = True
    is_valid.short_description = _('Is Valid')


@admin.register(QRShareToken)
class QRShareTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'pet', 'created_at', 'used', 'is_valid_display')
    list_filter = ('created_at', 'used')
    search_fields = ('token', 'pet__name')
    readonly_fields = ('is_valid_display',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('QR Share Token'), {
            'fields': ('pet',)
        }),
        (_('Status'), {
            'fields': ('used', 'is_valid_display')
        }),
    )

    def is_valid_display(self, obj):
        return obj.is_valid()

    is_valid_display.boolean = True
    is_valid_display.short_description = _('Is Valid')


@admin.register(VetPetAccess)
class VetPetAccessAdmin(admin.ModelAdmin):
    list_display = ('vet', 'pet', 'created_at', 'expires_at', 'granted_by', 'is_active_display')
    list_filter = ('created_at', 'expires_at', 'granted_by')
    search_fields = ('vet__clinic_name', 'pet__name')
    readonly_fields = ('is_active_display',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Access Info'), {
            'fields': ('vet', 'pet', 'granted_by')
        }),
        (_('Timing'), {
            'fields': ('expires_at', 'is_active_display')
        }),
    )

    def is_active_display(self, obj):
        return obj.is_active()

    is_active_display.boolean = True
    is_active_display.short_description = _('Is Active')
