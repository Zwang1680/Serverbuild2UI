# Generated by Django 3.0.5 on 2020-05-09 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0033_auto_20200509_0644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='networkinterface',
            old_name='device',
            new_name='networkdevice',
        ),
        migrations.RenameField(
            model_name='networkinterfaceconfiguration',
            old_name='interface',
            new_name='networkinterface',
        ),
        migrations.RenameField(
            model_name='puppetmachine',
            old_name='device',
            new_name='networkdevice',
        ),
        migrations.RemoveField(
            model_name='networkdevice',
            name='devicetype',
        ),
    ]