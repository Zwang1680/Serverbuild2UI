# Generated by Django 3.0.5 on 2020-07-28 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0046_auto_20200724_2356'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='elevation',
            field=models.FloatField(default=0.0, verbose_name='Elevation'),
        ),
    ]
