# Generated by Django 4.2.7 on 2025-03-23 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usanii', '0007_customer_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='is_approved',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
