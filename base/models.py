from django.db import models
from django.utils.crypto import get_random_string

from account.models import Dokter, Pasien

def random_pk():
    return get_random_string(6)

class JadwalDokter(models.Model):
    HARI_CHOICES = (
        ('senin', 'Senin'),
        ('selasa', 'Selasa'),
        ('rabu', 'Rabu'),
        ('kamis', 'Kamis'),
        ('jumat', 'Jumat'),
        ('sabtu', 'Sabtu'),
        ('minggu', 'Minggu'),
    )

    dokter = models.ForeignKey(Dokter, on_delete=models.CASCADE)
    hari = models.CharField(max_length=10, choices=HARI_CHOICES)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()


class Pendaftaran(models.Model):
    STATUS_CHOICES = (
        ("belum_bayar", "Belum Bayar"),
        ("antre", "Antre"),
        ("selesai", "Selesai"),
    )

    id = models.CharField(max_length=20, primary_key=True, default=random_pk, editable=False)
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    dokter = models.ForeignKey(Dokter, on_delete=models.CASCADE)
    asuransi = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="belum_bayar")
    tanggal = models.DateField()
    no_antrean = models.IntegerField(default=None, blank=True, null=True)


class Pemeriksaan(models.Model):
    id = models.CharField(max_length=20, primary_key=True, default=random_pk, editable=False)
    pendaftaran = models.OneToOneField(Pendaftaran, on_delete=models.CASCADE)
    path_pdf = models.CharField(max_length=255, blank=True, null=True)
    token = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.pendaftaran.pasien.user.nama_lengkap
    


