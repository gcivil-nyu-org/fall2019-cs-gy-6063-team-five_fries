# Generated by Django 2.2.7 on 2019-11-30 23:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0019_apartment_is_rented'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='number_of_bed',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Bedrooms'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='rent_price',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100000)]),
        ),
    ]
