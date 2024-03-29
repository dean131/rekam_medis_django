# Generated by Django 3.2.23 on 2023-11-10 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pendaftaran',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('asuransi', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('belum_bayar', 'Belum Bayar'), ('antre', 'Antre'), ('selesai', 'Selesai')], default='belum_bayar', max_length=15)),
                ('tanggal', models.DateField()),
                ('no_antrean', models.IntegerField(blank=True, default=None, null=True)),
                ('dokter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.dokter')),
                ('pasien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.pasien')),
            ],
        ),
        migrations.CreateModel(
            name='Pemeriksaan',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('path_pdf', models.CharField(blank=True, max_length=255, null=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('pendaftaran', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.pendaftaran')),
            ],
        ),
        migrations.CreateModel(
            name='JadwalDokter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hari', models.CharField(choices=[('senin', 'Senin'), ('selasa', 'Selasa'), ('rabu', 'Rabu'), ('kamis', 'Kamis'), ('jumat', 'Jumat'), ('sabtu', 'Sabtu'), ('minggu', 'Minggu')], max_length=10)),
                ('jam_mulai', models.TimeField()),
                ('jam_selesai', models.TimeField()),
                ('dokter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.dokter')),
            ],
        ),
    ]
