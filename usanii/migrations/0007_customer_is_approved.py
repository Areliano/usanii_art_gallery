# Generated by Django 4.2.7 on 2025-03-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usanii', '0006_remove_reservation_date_remove_reservation_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
