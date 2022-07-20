# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='hostname',
            field=models.CharField(unique=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mac',
            field=models.CharField(unique=True, max_length=17),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mirrorbase',
            field=models.URLField(max_length=512),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition',
            field=models.CharField(max_length=128, choices=[(b'auto', b'Automatic - CentOS will choose for you'), (b'lcogt', b'LCOGT - LCOGT default partition scheme'), (b'prompt', b'Prompt - You will be prompted')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='site',
            field=models.CharField(max_length=3, choices=[(b'bpl', b'BPL - Santa Barbara Back Parking Lot'), (b'coj', b'COJ - Siding Spring, Australia'), (b'cpt', b'CPT - SAAO Sutherland, South Africa'), (b'elp', b'ELP - McDonald Observatory, Texas'), (b'lpl', b'LPL - Liverpool, England'), (b'lsc', b'LSC - Cerro Tololo, Chile'), (b'mfg', b'MFG - Manufacturing'), (b'ngq', b'NGQ - Tibet'), (b'ogg', b'OGG - Haleakala, Hawaii'), (b'ptr', b'PTR - Photon Ranch, California'), (b'sba', b'SBA - Santa Barbara, California'), (b'sqa', b'SQA - Sedgwick Reserve, California'), (b'tfn', b'TFN - Tenerife'), (b'wtf', b'WTF - Warehouse Test Facility')]),
        ),
    ]
