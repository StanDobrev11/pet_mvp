# Generated by Django 5.2 on 2025-05-06 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0006_alter_medicalexaminationrecord_blood_test_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medicalexaminationrecord',
            old_name='fecal_exam',
            new_name='fecal_test',
        ),
    ]
