from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _

from pet_mvp.common.mixins import TimeStampMixin
from pet_mvp.medicine.models import Vaccine, BloodTest, Urinalysis, FecalExam, Medication
from pet_mvp.pets.models import Pet




class BaseRecord(TimeStampMixin):
    class Meta:
        abstract = True

    date_of_entry = models.DateField(
        verbose_name=_('Date of the entry'),
    )

    # doctor = models.ForeignKey(
    #     to=Doctor,
    #     on_delete=models.DO_NOTHING,
    # )
    doctor = models.CharField(
        max_length=100,
    )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )


class RabiesAntibodyTestRecord(BaseRecord):
    declaration = models.TextField(
        default=_('I, the undersigned, confirm that I have seen an official record stating that the rabies antibody '
                  'titration test performed at an EU-approved laboratory on a sample of blood collected on the '
                  'date mentioned below from the above described animal proved a response to anti-rabies vaccination '
                  'at a level of serum neutralising antibody equal to or greater than 0.5 IU/ml.')
    )

    sample_collected_on = models.DateField(
        verbose_name=_('Sample collected on'),
    )


class ClinicalExaminationRecord(BaseRecord):
    declaration = models.TextField(
        default=_('The animal show no signs of diseases and is fit to be transported for the intended journey')
    )


class LegalisationRecord(BaseRecord):
    legalising_body = models.TextField(
        verbose_name=_('Legalising body')
    )


class OtherRecord(TimeStampMixin):
    text_field = models.TextField()

    # doctor = models.ForeignKey(
    #     to=Doctor,
    #     on_delete=models.DO_NOTHING,
    # )

    pet = models.ForeignKey(
        to=Pet,
        on_delete=models.CASCADE
    )


class MedicalExaminationRecord(BaseRecord):
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
        to=Medication,
        related_name='examinations_medications',
        verbose_name=_('Medications Prescribed'),
        blank=True,
    )

    vaccinations = models.ManyToManyField(
        to=Vaccine,
        related_name='examinations_vaccinations',
        verbose_name=_('Vaccination Applied'),
        blank=True,
    )

    # vaccinations = models.ManyToManyField(
    #     to=OtherVaccination,
    #     related_name='examinations_other_vaccinations',
    #     verbose_name=_('Vaccination'),
    #     blank=True,
    # )
    #
    # rabies_vaccinations = models.ManyToManyField(
    #     to=RabiesVaccination,
    #     related_name='examinations_rabies_vaccinations',
    #     verbose_name=_('Rabies Vaccination'),
    #     blank=True,
    # )
    #
    # rabies_antibody_tests = models.ManyToManyField(
    #     to=RabiesAntibodyTestRecord,
    #     related_name='examinations_rabies_antibody',
    #     verbose_name=_('Rabies Antibody Tests'),
    #     blank=True,
    # )
    #
    # anti_parasite_treatments = models.ManyToManyField(
    #     to=OtherAntiParasiteTreatment,
    #     related_name='examinations_other_parasites',
    #     verbose_name=_('Parasites Treatments'),
    #     blank=True,
    # )
    #
    # echino_parasite_treatments = models.ManyToManyField(
    #     to=AntiEchinococcusTreatment,
    #     related_name='examinations_echino_parasites',
    #     verbose_name=_('Anti Echinococcus Treatments'),
    #     blank=True,
    # )
    #
    # clinical_examination_records = models.ManyToManyField(
    #     to=ClinicalExaminationRecord,
    #     related_name='examinations_clinical_record',
    #     verbose_name=_('Clinical Record'),
    #     blank=True,
    # )
    #
    # legalisations = models.ManyToManyField(
    #     to=LegalisationRecord,
    #     related_name='examinations_legalisations',
    #     verbose_name=_('Legalisation'),
    #     blank=True,
    # )
    #
    # others = models.ManyToManyField(
    #     to=OtherRecord,
    #     related_name='examinations_other_records',
    #     verbose_name=_('Other Records'),
    #     blank=True,
    # )

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
