# Generated by Django 5.1.1 on 2024-10-04 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
