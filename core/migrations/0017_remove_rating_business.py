# Generated by Django 4.2 on 2023-05-14 01:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_rating_warehouse_rating_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='business',
        ),
    ]
