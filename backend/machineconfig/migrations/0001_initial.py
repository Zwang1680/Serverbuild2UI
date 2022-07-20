# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac', models.CharField(max_length=17)),
                ('site', models.CharField(max_length=3, choices=[(b'bpl', b'BPL - Santa Barbara Back Parking Lot'), (b'coj', b'COJ - Siding Spring, Australia'), (b'cpt', b'CPT - SAAO Sutherland, South Africa'), (b'elp', b'ELP - McDonald Observatory, Texas'), (b'lpl', b'LPL - Liverpool, England'), (b'lsc', b'LSC - Cerro Tololo, Chile'), (b'ngq', b'NGQ - Tibet'), (b'ogg', b'OGG - Haleakala, Hawaii'), (b'sba', b'SBA - Santa Barbara, California'), (b'sqa', b'SQA - Sedgwick Reserve, California'), (b'tfn', b'TFN - Tenerife')])),
                ('osmajor', models.CharField(max_length=1, choices=[(b'5', b'5'), (b'6', b'6'), (b'7', b'7')])),
                ('arch', models.CharField(max_length=6, choices=[(b'i386', b'i386'), (b'x86_64', b'x86_64')])),
                ('netconf', models.CharField(max_length=6, choices=[(b'dhcp', b'dhcp'), (b'static', b'static')])),
                ('netdev', models.CharField(max_length=32)),
                ('hostname', models.CharField(max_length=128)),
                ('ipaddress', models.CharField(max_length=128)),
                ('netmask', models.CharField(max_length=128)),
                ('gateway', models.CharField(max_length=128)),
                ('nameserver', models.CharField(max_length=128)),
                ('partition', models.CharField(max_length=128)),
                ('puppetmaster', models.CharField(max_length=128)),
                ('ntpserver', models.CharField(max_length=128)),
                ('mirrorbase', models.URLField()),
            ],
            options={
                'ordering': ['site', 'mac'],
            },
            bases=(models.Model,),
        ),
    ]
