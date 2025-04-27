from django.db import models
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.drugs.models import Vaccine, BloodTest, Urinalysis, FecalExam
from pet_mvp.pets.models import Pet


class VaccinationRecord(TimeStampMixin):

    batch_number = models.CharField(
        max_length=50,
        verbose_name=_('Batch number')
    )

    manufacturer = models.CharField(
        max_length=50,
        verbose_name=_('Manufacturer'),
    )

    manufacture_date = models.DateField(
        verbose_name=_('Manufacture date')
    )

    date_of_vaccination = models.DateField(
        verbose_name=_('Date of vaccination'),
    )

    valid_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Valid from')
    )

    valid_until = models.DateField(
        verbose_name=_('Valid until')
    )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE,
        related_name='vaccine_records',
    )

    vaccine = models.ForeignKey(
        to=Vaccine,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f'{self.vaccine.name} vaccine. Valid untill {self.valid_until}.'


class MedicationRecord(TimeStampMixin):
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


class MedicalExaminationRecord(TimeStampMixin):
    date_of_entry = models.DateField(
        verbose_name=_('Date of the entry'),
    )

    doctor = models.CharField(
        max_length=100,
    )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )

    reason_for_visit = models.TextField(
        verbose_name=_('Reason for visit'),
        help_text=_('Description of the problem or reason for the visit')
    )

    general_health = models.TextField(
        verbose_name=_('General health'),
        blank=True,
        null=True
    )

    body_condition_score = models.IntegerField(
        verbose_name=_('Body Condition Score (1-9)'),
        help_text=_('Assessment of body condition (1 = underweight, 9 = obese)'),
        blank=True,
        null=True
    )

    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_('Temperature (°C)'),
        help_text=_('Body temperature of the animal'),
        blank=True,
        null=True
    )

    heart_rate = models.IntegerField(
        verbose_name=_('Heart rate (bpm)'),
        help_text=_('Heart rate in beats per minute'),
        blank=True,
        null=True
    )

    respiratory_rate = models.IntegerField(
        verbose_name=_('Respiratory rate'),
        help_text=_('Respiratory rate in breaths per minute'),
        blank=True,
        null=True
    )

    mucous_membrane_color = models.CharField(
        max_length=50,
        verbose_name=_('Mucous Membrane Color'),
        blank=True,
        null=True
    )

    hydration_status = models.CharField(
        max_length=50,
        verbose_name=_('Hydration Status'),
        blank=True,
        null=True
    )

    skin_and_coat_condition = models.TextField(
        verbose_name=_('Skin and Coat Condition'),
        blank=True,
        null=True
    )

    teeth_and_gums = models.TextField(
        verbose_name=_('Teeth and Gums'),
        blank=True,
        null=True
    )

    eyes_ears_nose = models.TextField(
        verbose_name=_('Eyes, Ears, and Nose'),
        blank=True,
        null=True
    )

    medication = models.ForeignKey(
        to=MedicationRecord,
        on_delete=models.CASCADE,
        related_name='examinations',
        verbose_name=_('Medications Prescribed'),
        blank=True,
    )

    vaccination = models.ForeignKey(
        to=VaccinationRecord,
        on_delete=models.CASCADE,
        related_name='examinations',
        verbose_name=_('Vaccination Applied'),
        blank=True,
    )

    blood_test = models.OneToOneField(
        to=BloodTest,
        verbose_name=_('Blood Test'),
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    urine_test = models.OneToOneField(
        to=Urinalysis,
        verbose_name=_('Urine Analysis'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    fecal_exam = models.OneToOneField(
        to=FecalExam,
        verbose_name=_('Fecal Analysis'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    treatment_performed = models.TextField(
        verbose_name=_('Treatment Carried Out'),
        help_text=_('Description of the Treatment'),
    )

    diagnosis = models.TextField(
        verbose_name=_('Diagnosis'),
        help_text=_('Description of the final diagnosis'),
        blank=True,
        null=True
    )

    follow_up = models.BooleanField(
        default=False,
        verbose_name=_('Follow-up Required?'),
    )

    notes = models.TextField(
        verbose_name=_('Examination Notes'),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Medical Record for {self.pet.name} on {self.date_of_entry}"
