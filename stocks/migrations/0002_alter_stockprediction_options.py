# Generated by Django 5.0 on 2025-07-28 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="stockprediction",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "株価予想",
                "verbose_name_plural": "株価予想",
            },
        ),
    ]
