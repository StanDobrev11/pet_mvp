from django.contrib import admin

from pet_mvp.common.models import Testimonial


# Register your models here.
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    pass
