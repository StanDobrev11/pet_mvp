# Generated by Django 5.2 on 2025-05-09 03:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0010_medicalexaminationrecord_clinic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicationrecord',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='vaccinationrecord',
            name='date_of_vaccination',
            field=models.DateField(default=datetime.date.today, verbose_name='Date of vaccination'),
        ),
        migrations.AlterField(
            model_name='vaccinationrecord',
            name='valid_from',
            field=models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Valid from'),
        ),
    ]
