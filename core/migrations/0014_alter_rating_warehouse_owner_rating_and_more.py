# Generated by Django 4.2 on 2023-05-10 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_rating_business_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='warehouse_owner_rating',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='warehouse_owner_review',
            field=models.TextField(blank=True),
        ),
    ]
