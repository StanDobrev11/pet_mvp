from django.db import models

# Create your models here.
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.city}"