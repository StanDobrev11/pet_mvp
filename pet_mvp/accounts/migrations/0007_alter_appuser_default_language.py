# Generated by Django 5.2 on 2025-05-29 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_appuser_is_approved_alter_appuser_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='default_language',
            field=models.CharField(choices=[('bg', 'BG'), ('en', 'EN')], default='bg', verbose_name='Default language'),
        ),
    ]
