# Generated by Django 4.2.7 on 2025-03-23 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usanii', '0010_alter_customer_date_alter_customer_event_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='event',
            field=models.CharField(default='Unknown Event', max_length=255),
        ),
        migrations.AlterField(
            model_name='customer',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='customer',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
