# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0004_auto_20150819_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='arch',
            field=models.CharField(default=b'x86_64', max_length=6, verbose_name=b'Architecture', choices=[(b'i386', b'i386'), (b'x86_64', b'x86_64')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='gateway',
            field=models.GenericIPAddressField(null=True, verbose_name=b'Gateway', protocol='ipv4'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='hostname',
            field=models.CharField(unique=True, max_length=128, verbose_name=b'Hostname'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='ipaddress',
            field=models.GenericIPAddressField(null=True, verbose_name=b'IP Address', protocol='ipv4'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mac',
            field=models.CharField(unique=True, max_length=17, verbose_name=b'MAC Address'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mirrorbase',
            field=models.URLField(max_length=512, null=True, verbose_name=b'CentOS Package Mirror Prefix'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='nameserver',
            field=models.CharField(max_length=128, null=True, verbose_name=b'Nameserver'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='netconf',
            field=models.CharField(default=b'dhcp', max_length=6, verbose_name=b'Method', choices=[(b'dhcp', b'dhcp'), (b'static', b'static')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='netdev',
            field=models.CharField(default=b'eth0', max_length=32, verbose_name=b'Device'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='netmask',
            field=models.GenericIPAddressField(null=True, verbose_name=b'Netmask', protocol='ipv4'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='ntpserver',
            field=models.CharField(max_length=128, null=True, verbose_name=b'NTP Server'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='osmajor',
            field=models.CharField(default=b'6', max_length=1, verbose_name=b'CentOS Release', choices=[(b'5', b'5'), (b'6', b'6'), (b'7', b'7')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition',
            field=models.CharField(default=b'auto', max_length=128, verbose_name=b'Partition Scheme', choices=[(b'auto', b'Automatic - CentOS will choose for you'), (b'lcogt', b'LCOGT - LCOGT default partition scheme'), (b'prompt', b'Prompt - You will be prompted'), (b'custom', b'Custom - Custom partition scheme (advanced!)')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition_custom',
            field=models.TextField(default=b'', verbose_name=b'Custom Partitioning'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='puppetmaster',
            field=models.CharField(max_length=128, null=True, verbose_name=b'PuppetMaster Hostname'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='rebuild',
            field=models.CharField(default=b'yes', max_length=4, verbose_name=b'Rebuild at next boot', choices=[(b'yes', b'Yes - Rebuild automatically at next boot'), (b'no', b'No - Do not rebuild automatically at next boot')]),
        ),
        migrations.AlterField(
            model_name='machine',
            name='site',
            field=models.CharField(default=b'sba', max_length=3, verbose_name=b'LCOGT Site', choices=[(b'bpl', b'BPL - Santa Barbara Back Parking Lot'), (b'coj', b'COJ - Siding Spring, Australia'), (b'cpt', b'CPT - SAAO Sutherland, South Africa'), (b'elp', b'ELP - McDonald Observatory, Texas'), (b'lpl', b'LPL - Liverpool, England'), (b'lsc', b'LSC - Cerro Tololo, Chile'), (b'mfg', b'MFG - Manufacturing'), (b'ngq', b'NGQ - Tibet'), (b'ogg', b'OGG - Haleakala, Hawaii'), (b'ptr', b'PTR - Photon Ranch, California'), (b'sba', b'SBA - Santa Barbara, California'), (b'sqa', b'SQA - Sedgwick Reserve, California'), (b'tfn', b'TFN - Tenerife'), (b'wtf', b'WTF - Warehouse Test Facility')]),
        ),
    ]
