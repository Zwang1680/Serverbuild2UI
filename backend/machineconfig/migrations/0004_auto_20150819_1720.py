# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0003_machine_rebuild'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='partition_custom',
            field=models.TextField(default=b''),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition',
            field=models.CharField(max_length=128, choices=[(b'auto', b'Automatic - CentOS will choose for you'), (b'lcogt', b'LCOGT - LCOGT default partition scheme'), (b'prompt', b'Prompt - You will be prompted'), (b'custom', b'Custom - Custom partition scheme (advanced!)')]),
        ),
    ]
