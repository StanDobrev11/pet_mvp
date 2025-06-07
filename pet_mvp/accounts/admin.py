from django.contrib import admin
from pet_mvp.accounts.models import AppUser, Owner, Clinic
from django.utils.translation import gettext_lazy as _
class OwnerInline(admin.StackedInline):
    model = Owner
    can_delete = False
    fk_name = 'user'

class ClinicInline(admin.StackedInline):
    model = Clinic
    can_delete = False
    fk_name = 'user'


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_owner', 'is_active', 'default_language')
    search_fields = ('email', 'phone_number', 'city', 'country')
    list_filter = ('is_owner', 'is_active')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if obj.is_owner:
            return [OwnerInline(self.model, self.admin_site)]
        else:
            return [ClinicInline(self.model, self.admin_site)]
