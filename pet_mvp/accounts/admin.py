from django.contrib import admin

from pet_mvp.accounts.models import AppUser, Owner, Clinic

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_owner=True)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            return [field for field in fields if field not in ["clinic_name", "clinic_address"]]
        return fields


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_owner=False)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            return [field for field in fields if field not in ["first_name", "last_name"]]
        return fields
