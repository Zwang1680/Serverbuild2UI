# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0005_auto_20150819_2351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='mirrorbase',
        ),
        migrations.AddField(
            model_name='machine',
            name='use_local_mirror',
            field=models.BooleanField(default=True, verbose_name=b'Use Local CentOS Package Mirror'),
        ),
    ]
