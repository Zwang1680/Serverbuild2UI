# Generated by Django 3.0.5 on 2020-05-23 07:31

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0037_auto_20200522_0535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='nameserver',
        ),
        migrations.AddField(
            model_name='site',
            name='dnsservers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.GenericIPAddressField(protocol='ipv4', verbose_name='DNS Servers'), default=list, size=None),
        ),
    ]
