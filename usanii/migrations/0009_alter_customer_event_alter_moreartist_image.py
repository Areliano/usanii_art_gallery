# Generated by Django 4.2.7 on 2025-03-23 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usanii', '0008_alter_customer_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='event',
            field=models.CharField(blank=True, default='Opening Event', max_length=300),
        ),
        migrations.AlterField(
            model_name='moreartist',
            name='image',
            field=models.ImageField(default='moreartist.jpg', upload_to='moreartist'),
        ),
    ]
