# Generated by Django 5.2 on 2025-05-19 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0008_remove_pet_breed_bg_remove_pet_breed_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='species_bg',
            field=models.CharField(choices=[('dog', 'Dog'), ('cat', 'Cat')], max_length=50, null=True, verbose_name='Species'),
        ),
        migrations.AddField(
            model_name='pet',
            name='species_en',
            field=models.CharField(choices=[('dog', 'Dog'), ('cat', 'Cat')], max_length=50, null=True, verbose_name='Species'),
        ),
    ]
