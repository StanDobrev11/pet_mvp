from django.contrib import admin
from pet_mvp.accounts.models import AppUser, Owner, Clinic

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'first_name', 'last_name')
    search_fields = ('user__email', 'first_name', 'last_name')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'clinic_name', 'clinic_address', 'is_approved')
    search_fields = ('user__email', 'clinic_name', 'clinic_address')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
