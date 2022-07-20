# Generated by Django 2.0.2 on 2019-05-24 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0015_auto_20180221_2100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='ntpserver',
        ),
        migrations.AlterField(
            model_name='history',
            name='ipaddress',
            field=models.GenericIPAddressField(protocol='ipv4', verbose_name='IP Address'),
        ),
        migrations.AlterField(
            model_name='history',
            name='success',
            field=models.BooleanField(default=False, verbose_name='Success'),
        ),
        migrations.AlterField(
            model_name='history',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Timestamp'),
        ),
        migrations.AlterField(
            model_name='history',
            name='url',
            field=models.CharField(max_length=64, verbose_name='Request'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='arch',
            field=models.CharField(choices=[('i386', 'i386'), ('x86_64', 'x86_64')], default='x86_64', max_length=6, verbose_name='Architecture'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='boot_mode',
            field=models.CharField(choices=[('local', 'Boot from local disk'), ('rebuild', 'Rebuild at next boot'), ('rescue', 'Rescue at next boot')], default='rebuild', max_length=16, verbose_name='Boot mode'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='hostname',
            field=models.CharField(max_length=128, unique=True, verbose_name='Hostname'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='ipaddress',
            field=models.GenericIPAddressField(null=True, protocol='ipv4', verbose_name='IP Address'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mac',
            field=models.CharField(max_length=17, unique=True, verbose_name='MAC Address'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='netconf',
            field=models.CharField(choices=[('dhcp', 'dhcp'), ('static', 'static')], default='dhcp', max_length=6, verbose_name='Method'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='netdev',
            field=models.CharField(default='eth0', max_length=32, verbose_name='Device'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='osmajor',
            field=models.CharField(choices=[('5', '5'), ('6', '6'), ('7', '7')], default='7', max_length=1, verbose_name='CentOS Release'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='packagemirror',
            field=models.CharField(default='', max_length=256, verbose_name='Package Mirror URL'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition',
            field=models.CharField(choices=[('auto', 'Automatic - CentOS will choose for you'), ('docknode', 'Docker node standard partition scheme'), ('lcogt', 'LCOGT - LCOGT default partition scheme'), ('prompt', 'Prompt - You will be prompted'), ('pubsubdb', 'PubsubDB - PubsubDB standard partition scheme'), ('simple', 'Simple - All space in one large partition'), ('simple-8swap', 'Simple + 8GB swap - All space in one large partition + 8GB swap'), ('simple-8swap-20var', 'Simple + 8GB swap + 20GB /var - All space in one large partition + 8GB swap + 20GB /var'), ('custom', 'Custom - Custom partition scheme (advanced!)')], default='auto', max_length=128, verbose_name='Partition Scheme'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='partition_custom',
            field=models.TextField(default='', verbose_name='Custom Partitioning'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='puppetmaster',
            field=models.CharField(max_length=128, null=True, verbose_name='PuppetMaster Hostname'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='site',
            field=models.CharField(choices=[('bpl', 'BPL - Santa Barbara Back Parking Lot'), ('coj', 'COJ - Siding Spring, Australia'), ('cpt', 'CPT - SAAO Sutherland, South Africa'), ('elp', 'ELP - McDonald Observatory, Texas'), ('lpl', 'LPL - Liverpool, England'), ('lsc', 'LSC - Cerro Tololo, Chile'), ('mfg', 'MFG - Manufacturing'), ('ngq', 'NGQ - Tibet'), ('ogg', 'OGG - Haleakala, Hawaii'), ('ptr', 'PTR - Photon Ranch, California'), ('sba', 'SBA - Santa Barbara, California'), ('sci', 'SCI - Science Domain, Santa Barbara, California'), ('sqa', 'SQA - Sedgwick Reserve, California'), ('tlv', 'TLV - Tel Aviv, Israel'), ('tfn', 'TFN - Tenerife'), ('wer', 'WER - Wayne Rosing'), ('wtf', 'WTF - Warehouse Test Facility')], default='sba', max_length=3, verbose_name='LCOGT Site'),
        ),
    ]
