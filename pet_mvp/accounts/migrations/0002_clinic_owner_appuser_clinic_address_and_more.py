# Generated by Django 5.2 on 2025-05-03 12:06

import pet_mvp.accounts.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
            ],
            options={
                'verbose_name': 'Clinic',
                'verbose_name_plural': 'Clinics',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.appuser',),
            managers=[
                ('objects', pet_mvp.accounts.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
            ],
            options={
                'verbose_name': 'Owner',
                'verbose_name_plural': 'Owners',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.appuser',),
            managers=[
                ('objects', pet_mvp.accounts.managers.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='appuser',
            name='clinic_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='appuser',
            name='clinic_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='appuser',
            name='country',
            field=models.CharField(default='Bulgaria', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appuser',
            name='is_owner',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
