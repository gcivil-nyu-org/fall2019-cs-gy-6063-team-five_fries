# Generated by Django 2.2.8 on 2019-12-04 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external', '0007_nyc311statistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='cachedsearch',
            name='locality',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]