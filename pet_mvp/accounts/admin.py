from django.contrib import admin

from pet_mvp.accounts.models import AppUser


# Register your models here.
@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            if obj.is_owner:
                # Show only owner-specific fields
                return [field for field in fields if field not in ["clinic_name", "clinic_address"]]
            else:
                # Show only clinic-specific fields
                return [field for field in fields if field not in ["first_name", "last_name"]]
        return fields
