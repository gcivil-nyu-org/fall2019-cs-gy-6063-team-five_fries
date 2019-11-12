# Generated by Django 2.2.7 on 2019-11-12 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_apartment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='estimated_rent_price_currency',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='last_estimated',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='zillow_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='zpid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]