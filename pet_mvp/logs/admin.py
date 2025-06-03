from django.contrib import admin

from pet_mvp.logs.models import PetAccessLog

# Register your models here.
@admin.register(PetAccessLog)
class PetAccessLogAdmin(admin.ModelAdmin):
    pass