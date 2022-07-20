# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0007_auto_20151021_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='boot_mode',
            field=models.CharField(default=b'rebuild', max_length=16, verbose_name=b'Boot mode', choices=[(b'local', b'Boot from local disk'), (b'rebuild', b'Rebuild at next boot'), (b'rescue', b'Rescue at next boot')]),
        ),
    ]
