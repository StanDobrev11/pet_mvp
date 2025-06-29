# Generated by Django 5.2 on 2025-05-25 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0011_pet_pending_owners'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='features',
            field=models.CharField(max_length=255, verbose_name='Features'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='features_bg',
            field=models.CharField(max_length=255, null=True, verbose_name='Features'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='features_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Features'),
        ),
    ]
