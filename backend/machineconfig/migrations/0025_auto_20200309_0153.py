# Generated by Django 3.0.4 on 2020-03-09 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machineconfig', '0024_site'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['code']},
        ),
    ]