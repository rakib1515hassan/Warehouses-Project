# Generated by Django 4.2 on 2023-05-03 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='storage_space_type',
        ),
        migrations.AddField(
            model_name='warehouse',
            name='storage_space_type',
            field=models.ManyToManyField(blank=True, null=True, to='core.storage_space_type'),
        ),
    ]
