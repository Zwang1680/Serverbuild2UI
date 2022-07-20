# Generated by Django 3.1.1 on 2020-10-02 17:14
# https://docs.djangoproject.com/en/3.1/topics/migrations/#data-migrations

from django.db import migrations

def combine_operatingsystem(apps, schema_editor):
    # We can't import the PuppetMachine model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    PuppetMachine = apps.get_model('machineconfig', 'PuppetMachine')
    for p in PuppetMachine.objects.all():
        p.operatingsystem = f'{p.ostype}-{p.osversion}-{p.arch}'
        p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0066_puppetmachine_operatingsystem'),
    ]

    operations = [
        migrations.RunPython(combine_operatingsystem),
    ]