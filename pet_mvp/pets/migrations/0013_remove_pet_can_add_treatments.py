# Generated by Django 5.2 on 2025-05-26 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0012_alter_pet_features_alter_pet_features_bg_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pet',
            name='can_add_treatments',
        ),
    ]
