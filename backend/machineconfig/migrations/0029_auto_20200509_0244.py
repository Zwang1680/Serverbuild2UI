# Generated by Django 3.0.5 on 2020-05-09 02:44

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0028_auto_20200321_0302'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.FileField(blank=True, max_length=256, upload_to='', verbose_name='Device Image')),
                ('information', models.TextField()),
                ('devicetype', models.CharField(choices=[('generic', 'Generic Network Device'), ('puppet', 'Puppet Managed Device')], max_length=32, verbose_name='Device Type')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Description')),
                ('mac', models.CharField(max_length=17, unique=True, verbose_name='MAC Address')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machineconfig.NetworkDevice')),
            ],
        ),
        migrations.AddField(
            model_name='machine',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='machine',
            name='last_boot_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='machine',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='site',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='domain',
            field=models.CharField(default='lco.gtn', max_length=64, verbose_name='Network Domain'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='PuppetMachine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ostype', models.CharField(choices=[('centos', 'CentOS'), ('proxmox', 'Proxmox VE')], default='centos', max_length=32, verbose_name='Operating System Type')),
                ('osversion', models.CharField(default='7', max_length=32, verbose_name='Operating System Version')),
                ('arch', models.CharField(choices=[('i386', 'i386'), ('x86_64', 'x86_64')], default='x86_64', max_length=32, verbose_name='Architecture')),
                ('partitionscheme', models.CharField(choices=[('auto', 'Automatic - CentOS will choose for you'), ('docknode', 'Docker node standard partition scheme'), ('lcogt', 'LCOGT - LCOGT default partition scheme'), ('prompt', 'Prompt - You will be prompted'), ('pubsubdb', 'PubsubDB - PubsubDB standard partition scheme'), ('simple', 'Simple - All space in one large partition'), ('simple-8swap', 'Simple + 8GB swap - All space in one large partition + 8GB swap'), ('simple-8swap-20var', 'Simple + 8GB swap + 20GB /var - All space in one large partition + 8GB swap + 20GB /var'), ('custom', 'Custom - Custom partition scheme (advanced!)')], max_length=32, verbose_name='Partition Scheme')),
                ('partitionscheme_custom', models.TextField(blank=True, verbose_name='Custom Partition Scheme')),
                ('boot_mode', models.CharField(choices=[('local', 'Boot from local disk'), ('rebuild', 'Rebuild at next boot'), ('rebuildalt', 'Rebuild at next boot (use alternate package mirror)'), ('rescue', 'Rescue at next boot')], max_length=32, verbose_name='Boot Mode')),
                ('lastboot_at', models.DateTimeField(blank=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machineconfig.NetworkDevice', verbose_name='Network Device')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterfaceConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipaddress', models.GenericIPAddressField(protocol='ipv4', verbose_name='IP Address')),
                ('hostname', models.CharField(max_length=256, verbose_name='Hostname')),
                ('aliases', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256, verbose_name='Hostname Alias'), blank=True, size=None)),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machineconfig.NetworkInterface')),
            ],
        ),
        migrations.AddField(
            model_name='networkdevice',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machineconfig.Site', verbose_name='Telescope Site'),
        ),
    ]
