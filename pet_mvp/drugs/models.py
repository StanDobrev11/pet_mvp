import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseMedication(models.Model):

    SUITABLE_FOR_CHOICES = [
        ('cat', _('Cat')),
        ('dog', _('Dog'))
    ]

    class Meta:
        abstract = True

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name of vaccine'),
        unique=True,
    )

    notes = models.TextField(
        verbose_name=_('Notes')
    )

    recommended_interval_days = models.PositiveIntegerField(
        verbose_name=_('Recommended interval (days)'),
        help_text=_(
            'Number of days after which the treatment/vaccine should be repeated. Leave blank if not applicable.'),
        null=True,
        blank=True
    )

    suitable_for = models.CharField(
        max_length=10,
        choices=SUITABLE_FOR_CHOICES,
        verbose_name=_('Suitable for'),
        help_text=_('Select whether is for cats or dogs.')
    )

    def __str__(self):
        return f'{self.name}'

    def get_recommended_interval(self):
        """Returns the recommended interval as a timedelta object (or None)."""
        if self.recommended_interval_days:
            return datetime.timedelta(days=self.recommended_interval_days)
        return None


# Create your models here.
class Vaccine(BaseMedication):
    core = models.BooleanField(
        default=False,
        verbose_name=_('Core vaccine')
    )


class Drug(BaseMedication):
    pass


class BaseTest(models.Model):
    class Meta:
        abstract = True

    result = models.TextField(
        verbose_name=_('Test Result'),
        help_text=_('Description of the test result')
    )
    date_conducted = models.DateField(
        verbose_name=_('Date Conducted'),
        help_text=_('Date when the test was conducted'),
        default=datetime.date.today,
    )
    additional_notes = models.TextField(
        verbose_name=_('Additional Notes'),
        blank=True,
        null=True,
        help_text=_('Optional notes or observations about the test')
    )

    @property
    def name(self):
        return ' Test'.join(self.__class__.__name__.split('Test'))

    def __str__(self):
        return f"{self.name} conducted on {self.date_conducted}"


class BloodTest(BaseTest):
    white_blood_cells = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('White Blood Cells (WBC)'),
        help_text=_('Count of white blood cells per microliter'),
        blank=True,
        null=True
    )
    red_blood_cells = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('Red Blood Cells (RBC)'),
        help_text=_('Count of red blood cells per microliter'),
        blank=True,
        null=True
    )
    hemoglobin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_('Hemoglobin Level (g/dL)'),
        help_text=_('Measurement of hemoglobin concentration'),
        blank=True,
        null=True
    )
    platelets = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('Platelets'),
        help_text=_('Platelet count per microliter'),
        blank=True,
        null=True
    )


class UrineTest(BaseTest):
    color = models.CharField(
        max_length=50,
        verbose_name=_('Color'),
        help_text=_('Color of the urine'),
        blank=True,
        null=True
    )
    clarity = models.CharField(
        max_length=50,
        verbose_name=_('Clarity'),
        help_text=_('Clarity of the urine, e.g., clear, cloudy'),
        blank=True,
        null=True
    )
    ph = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_('pH'),
        help_text=_('Urine pH level'),
        blank=True,
        null=True
    )
    specific_gravity = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        verbose_name=_('Specific Gravity'),
        help_text=_('Measurement of urine concentration'),
        blank=True,
        null=True
    )
    protein = models.CharField(
        max_length=50,
        verbose_name=_('Protein'),
        help_text=_('Presence of protein in urine'),
        blank=True,
        null=True
    )
    glucose = models.CharField(
        max_length=50,
        verbose_name=_('Glucose'),
        help_text=_('Presence of glucose in urine'),
        blank=True,
        null=True
    )
    red_blood_cells = models.CharField(
        max_length=50,
        verbose_name=_('Red Blood Cells'),
        help_text=_('Presence of red blood cells in urine'),
        blank=True,
        null=True
    )
    white_blood_cells = models.CharField(
        max_length=50,
        verbose_name=_('White Blood Cells'),
        help_text=_('Presence of white blood cells in urine'),
        blank=True,
        null=True
    )


class FecalTest(BaseTest):
    consistency = models.CharField(
        max_length=50,
        verbose_name=_('Consistency'),
        help_text=_('Consistency of the feces, e.g., firm, watery'),
        blank=True,
        null=True
    )
    parasites_detected = models.BooleanField(
        verbose_name=_('Parasites Detected'),
        default=False,
        help_text=_('Parasites Detected')
    )
    parasite_type = models.CharField(
        max_length=100,
        verbose_name=_('Type of Parasites'),
        blank=True,
        null=True,
        help_text=_('Type of detected parasites, if any')
    )
    blood_presence = models.BooleanField(
        verbose_name=_('Blood Presence in Stool'),
        default=False,
        help_text=_('Blood Presence in Stool')
    )
