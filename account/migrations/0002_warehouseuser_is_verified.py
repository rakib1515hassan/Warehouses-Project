# Generated by Django 4.2 on 2023-05-03 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]