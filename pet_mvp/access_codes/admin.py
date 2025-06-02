from django.contrib import admin
from django.utils import timezone

from pet_mvp.access_codes.models import PetAccessCode, QRShareToken, VetPetAccess


@admin.register(PetAccessCode)
class PetAccessCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('code', 'pet__name')
    readonly_fields = ('is_valid',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Access Code', {
            'fields': ('code', 'pet')
        }),
        ('Validity', {
            'fields': ('created_at', 'expires_at', 'is_valid')
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Is Valid'

@admin.register(QRShareToken)
class QRShareTokenAdmin(admin.ModelAdmin):
    pass

@admin.register(VetPetAccess)
class VetPetAccessAdmin(admin.ModelAdmin):
    pass