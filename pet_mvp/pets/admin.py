from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from pet_mvp.pets.models import Pet, Transponder, Tattoo


class TransponderInline(admin.TabularInline):
    model = Transponder
    extra = 0


class TattooInline(admin.TabularInline):
    model = Tattoo
    extra = 0


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'species', 'get_breed_display', 'sex', 'date_of_birth',
        'display_photo', 'passport_number', 'current_weight', 'can_add_vaccines', 'age'
    )
    list_filter = ('species', 'breed', 'sex', 'can_add_vaccines')
    search_fields = (
        'name', 'passport_number',
        'owners__email', 'owners__username',
        'pending_owners__email', 'pending_owners__username'
    )
    date_hierarchy = 'date_of_birth'
    filter_horizontal = ('owners', 'pending_owners')
    inlines = [TransponderInline, TattooInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name', 'species', 'breed', 'sex', 'date_of_birth',
                'color', 'features', 'current_weight', 'passport_number'
            )
        }),
        (_('Photo'), {
            'fields': ('photo',)
        }),
        (_('Permissions'), {
            'fields': ('can_add_vaccines',)
        }),
        (_('Ownership'), {
            'fields': ('owners', 'pending_owners')
        }),
    )

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                               obj.photo.url)
        return _("No Photo")

    display_photo.short_description = _('Photo')

    def age(self, obj):
        return obj.age

    age.short_description = _('Age')


@admin.register(Transponder)
class TransponderAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'date_of_application', 'date_of_reading', 'location')
    list_filter = ('date_of_application', 'date_of_reading')
    search_fields = ('code', 'pet__name')
    date_hierarchy = 'date_of_reading'


@admin.register(Tattoo)
class TattooAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'date_of_application', 'date_of_reading', 'location')
    list_filter = ('date_of_application', 'date_of_reading')
    search_fields = ('code', 'pet__name')
    date_hierarchy = 'date_of_reading'
