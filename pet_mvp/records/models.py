import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from pet_mvp.accounts.models import Clinic
from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.drugs.models import Vaccine, BloodTest, UrineTest, FecalTest, Drug
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
        default=datetime.date.today,
    )

    valid_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Valid from'),
        default=datetime.date.today,
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
        return _("{} - Valid to: {}").format(self.vaccine.name, self.valid_until)


class MedicationRecord(TimeStampMixin):
    
    date = models.DateField(
        verbose_name=_('Date of intake'),
        default=datetime.date.today,
    )
 
    valid_until = models.DateField(
        verbose_name=_('Valid Until'),
        help_text=_('Specify valid until date')
    )
    
    time = models.TimeField(
        verbose_name=_('Time of intake'),
        help_text=_('Time of intake'),
        null=True,
        blank=True,
    )

    dosage = models.CharField(
        max_length=50,
        verbose_name=_('Dosage'),
        help_text=_('Specify dosage, if different from reccomended'),
        blank=True,
    )
    
    manufacturer = models.CharField(
        max_length=50,
        verbose_name=_('Manufacturer')
    )
    
    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE,
        related_name='medication_records'
    )

    medication = models.ForeignKey(
        to=Drug,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return _("{} - Valid to: {}").format(self.medication.name, self.valid_until)


class MedicalExaminationRecord(TimeStampMixin):
    EXAM_TYPE_CHOICES = [
        ('primary', _('Primary Examination')),
        ('follow_up', _('Follow-up Examination')),
    ]

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        default='primary',
        verbose_name=_('Examination Type'),
        help_text=_('Indicates whether this is an initial examination or a follow-up')
    )

    date_of_entry = models.DateField(
        verbose_name=_('Date of the entry'),
        default=datetime.date.today,
    )

    doctor = models.CharField(
        max_length=100,
    )

    clinic = models.ForeignKey(
        to=Clinic,
        related_name='clinic_records',
        on_delete=models.CASCADE,
        verbose_name=_('Clinic'),
        help_text=_('Clinic where the examination was conducted'),
    )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE,
        related_name='examination_records'
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

    medications = models.ManyToManyField(
        to=MedicationRecord,
        related_name='examinations',
        verbose_name=_('Medications Prescribed'),
        blank=True,
    )

    vaccinations = models.ManyToManyField(
        to=VaccinationRecord,
        related_name='examinations',
        verbose_name=_('Vaccinations Applied'),
        blank=True,
    )

    blood_test = models.ForeignKey(
        to=BloodTest,
        verbose_name=_('Blood Test'),
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    urine_test = models.ForeignKey(
        to=UrineTest,
        verbose_name=_('Urine Analysis'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    fecal_test = models.ForeignKey(
        to=FecalTest,
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
        pet_name = self.pet.name if self.pet_id else _("Unknown Pet")
        date = self.date_of_entry if self.date_of_entry else _("Unknown Date")
        return _("Medical Record for {} on {}").format(pet_name, date)
