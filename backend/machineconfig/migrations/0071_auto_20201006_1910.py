# Generated by Django 3.1.1 on 2020-10-06 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0070_auto_20201006_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webcam',
            name='adminurl',
            field=models.URLField(max_length=1024, verbose_name='Webcam Administration Interface URL'),
        ),
        migrations.AlterField(
            model_name='webcam',
            name='imageurl',
            field=models.URLField(max_length=1024, verbose_name='Webcam Image Fetch URL'),
        ),
    ]
