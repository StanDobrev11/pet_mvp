# Generated by Django 5.2 on 2025-06-03 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0013_remove_pet_can_add_treatments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pet',
            name='pending_owners',
        ),
    ]
