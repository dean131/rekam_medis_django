# Generated by Django 3.2.23 on 2023-11-03 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_pendaftaran_poli'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendaftaran',
            name='waktu',
        ),
    ]
