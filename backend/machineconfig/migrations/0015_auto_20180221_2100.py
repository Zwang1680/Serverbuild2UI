# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-21 21:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0014_auto_20170504_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='partition',
            field=models.CharField(choices=[(b'auto', b'Automatic - CentOS will choose for you'), (b'docknode', b'Docker node standard partition scheme'), (b'lcogt', b'LCOGT - LCOGT default partition scheme'), (b'prompt', b'Prompt - You will be prompted'), (b'pubsubdb', b'PubsubDB - PubsubDB standard partition scheme'), (b'simple', b'Simple - All space in one large partition'), (b'simple-8swap', b'Simple + 8GB swap - All space in one large partition + 8GB swap'), (b'simple-8swap-20var', b'Simple + 8GB swap + 20GB /var - All space in one large partition + 8GB swap + 20GB /var'), (b'custom', b'Custom - Custom partition scheme (advanced!)')], default=b'auto', max_length=128, verbose_name=b'Partition Scheme'),
        ),
    ]