from django.contrib import admin
from django.utils.html import format_html

from pet_mvp.pets.models import Pet, BaseMarking, Transponder, Tattoo


class TransponderInline(admin.TabularInline):
    model = Transponder
    extra = 0


class TattooInline(admin.TabularInline):
    model = Tattoo
    extra = 0


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'sex', 'date_of_birth', 'display_photo', 'passport_number')
    list_filter = ('species', 'breed', 'sex')
    search_fields = ('name', 'passport_number', 'owners__email', 'owners__username')
    date_hierarchy = 'date_of_birth'
    filter_horizontal = ('owners',)
    inlines = [TransponderInline, TattooInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'species', 'breed', 'sex', 'date_of_birth', 'color', 'features', 'current_weight', 'passport_number')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Permissions', {
            'fields': ('can_add_vaccines', 'can_add_treatments')
        }),
        ('Ownership', {
            'fields': ('owners',)
        }),
    )
    
    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'


@admin.register(Transponder)
class TransponderAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'date_of_reading', 'location')
    list_filter = ('date_of_reading',)
    search_fields = ('code', 'pet__name')
    date_hierarchy = 'date_of_reading'


@admin.register(Tattoo)
class TattooAdmin(admin.ModelAdmin):
    list_display = ('code', 'pet', 'date_of_application', 'location')
    list_filter = ('date_of_application',)
    search_fields = ('code', 'pet__name')
    date_hierarchy = 'date_of_application'
