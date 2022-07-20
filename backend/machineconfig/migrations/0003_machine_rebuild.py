# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0002_auto_20150611_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='rebuild',
            field=models.CharField(default='no', max_length=4, choices=[(b'yes', b'Yes - Rebuild automatically at next boot'), (b'no', b'No - Do not rebuild automatically at next boot')]),
            preserve_default=False,
        ),
    ]
