from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from pet_mvp.accounts.models import AppUser, Owner, Clinic, Groomer, Store


class OwnerInline(admin.StackedInline):
    model = Owner
    can_delete = False
    fk_name = 'user'


class ClinicInline(admin.StackedInline):
    model = Clinic
    can_delete = False
    fk_name = 'user'


class GroomerInline(admin.StackedInline):
    model = Groomer
    can_delete = False
    fk_name = 'user'


class StoreInline(admin.StackedInline):
    model = Store
    can_delete = False
    fk_name = 'user'


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_owner', 'is_clinic', 'is_groomer', 'is_store', 'is_active', 'default_language')
    search_fields = ('email', 'phone_number', 'city', 'country')
    list_filter = ('is_owner', 'is_clinic', 'is_groomer', 'is_store', 'is_active', 'default_language')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        inlines = []

        if obj.is_owner:
            inlines.append(OwnerInline(self.model, self.admin_site))
        if obj.is_clinic:
            inlines.append(ClinicInline(self.model, self.admin_site))
        if obj.is_groomer:
            inlines.append(GroomerInline(self.model, self.admin_site))
        if obj.is_store:
            inlines.append(StoreInline(self.model, self.admin_site))

        return inlines


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_approved')
    search_fields = ('name', 'address', 'user__email')
    list_filter = ('is_approved',)


@admin.register(Groomer)
class GroomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_approved')
    search_fields = ('name', 'address', 'user__email')
    list_filter = ('is_approved',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_approved')
    search_fields = ('name', 'address', 'user__email')
    list_filter = ('is_approved',)
