# Generated by Django 5.2 on 2025-06-05 20:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_codes', '0007_qrsharetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='VetPetAccess',
            name='vet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.clinic'),
        ),
    ]
