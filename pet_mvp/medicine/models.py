from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.pets.models import Pet


# Create your models here.
class Vaccine(models.Model):
    manufacturer_and_name = models.CharField(
        max_length=50,
        verbose_name=_('Manufacturer and name of vaccine')
    )

    batch_number = models.CharField(
        max_length=50,
        verbose_name=_('Batch number')
    )

class BaseVaccination(TimeStampMixin):
    class Meta:
        abstract = True

    manufacturer_and_name = models.CharField(
        max_length=50,
        verbose_name=_('Manufacturer and name of vaccine')
    )

    batch_number = models.CharField(
        max_length=50,
        verbose_name=_('Batch number')
    )

    date_of_vaccination = models.DateField(
        verbose_name=_('Date of vaccination')
    )

    valid_until = models.DateField(
        verbose_name=_('Valid until')
    )

    # doctor = models.ForeignKey(
    #     to=Doctor,
    #     on_delete=models.DO_NOTHING,
    # )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.manufacturer_and_name}'


class RabiesVaccination(BaseVaccination):
    valid_from = models.DateField(
        verbose_name=_('Valid from')
    )


class OtherVaccination(BaseVaccination):
    pass


class BaseTreatment(TimeStampMixin):
    class Meta:
        abstract = True

    manufacturer_and_name = models.CharField(
        max_length=50,
        verbose_name=_('Manufacturer and name of product')
    )

    date = models.DateField(
        verbose_name=_('Date')
    )

    time = models.TimeField(
        help_text=_('Time'),
        null=True,
        blank=True,
    )

    dosage = models.CharField(
        max_length=50,
        verbose_name=_('Dosage'),
        help_text=_('Specify dosage, e.g. "5mg twice a day"')
    )

    duration = models.CharField(
        max_length=50,
        verbose_name=_('Duration'),
        help_text=_('Specify duration, e.g. "7 days"')
    )

    notes = models.TextField(
        verbose_name=_('Additional Notes'),
        blank=True,
        null=True
    )

    # doctor = models.ForeignKey(
    #     to=Doctor,
    #     on_delete=models.DO_NOTHING,
    # )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.manufacturer_and_name}'


class Medication(BaseTreatment):
    pass


class AntiEchinococcusTreatment(BaseTreatment):
    pass


class OtherAntiParasiteTreatment(BaseTreatment):
    pass



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
