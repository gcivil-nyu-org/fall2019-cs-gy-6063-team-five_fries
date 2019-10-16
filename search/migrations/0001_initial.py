# Generated by Django 2.2.4 on 2019-10-14 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CraigslistLocation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("c_id", models.CharField(max_length=200)),
                ("name", models.CharField(max_length=200)),
                ("date_time", models.DateTimeField()),
                ("url", models.URLField()),
                ("price", models.CharField(max_length=200)),
                ("where", models.CharField(max_length=200)),
                ("has_image", models.BooleanField(default=False)),
                ("has_map", models.BooleanField(default=False)),
                (
                    "lat",
                    models.DecimalField(
                        blank=True, decimal_places=16, max_digits=22, null=True
                    ),
                ),
                (
                    "lon",
                    models.DecimalField(
                        blank=True, decimal_places=16, max_digits=22, null=True
                    ),
                ),
            ],
        )
    ]