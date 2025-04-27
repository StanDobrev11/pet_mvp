from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.pets.models import Pet


# Create your models here.
class Vaccine(models.Model):

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name of vaccine'),
        unique=True,
    )

    core = models.BooleanField(
        default=False,
        verbose_name=_('Core vaccine')
    )

    notes = models.TextField(
        verbose_name=_('Notes')
    )


class Drug(models.Model):

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name of vaccine'),
        unique=True,
    )

    notes = models.TextField(
        verbose_name=_('Notes')
    )


class BaseTest(models.Model):
    class Meta:
        abstract = True

    test_name = models.CharField(max_length=100, verbose_name=_('Test Name'))
    result = models.TextField(verbose_name=_('Test Result'))

    def __str__(self):
        return self.test_name


class BloodTest(BaseTest):
    pass


class Urinalysis(BaseTest):
    pass


class FecalExam(BaseTest):
    pass
