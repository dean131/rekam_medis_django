from django.db import models

from account.models import User, Dokter, Pasien, Apoteker, Resepsionis


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
    waktu = models.CharField(max_length=15)


class Pendaftaran(models.Model):
    STATUS_CHOICES = (
        ("belum_bayar", "Belum Bayar"),
        ("antre", "Antre"),
        ("selesai", "Selesai"),
    )

    POLI_CHOICES = (
        ("umum", "Umum"),
        ("mulut/gigi", "Mulut/Gigi"),
        ("lansia", "Lansia"),
        ("pkpr", "PKPR"),
        ("kia/kb", "KIA/KB"),
        ("mtbm/mtbs", "MTBM/MTBS"),
    )

    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    dokter = models.ForeignKey(Dokter, on_delete=models.CASCADE)
    tanggal = models.DateField()
    poli = models.CharField(max_length=50, choices=POLI_CHOICES)
    asuransi = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="belum_bayar")


class Pemeriksaan(models.Model):
    pendaftaran = models.ForeignKey(Pendaftaran, on_delete=models.CASCADE)
    keluhan = models.TextField()
    suhu_tubuh = models.DecimalField(max_digits=5, decimal_places=2)
    tensi_darah = models.CharField(max_length=10)
    berat_badan = models.DecimalField(max_digits=5, decimal_places=2)
    tinggi_badan = models.DecimalField(max_digits=5, decimal_places=2)
    nadi_per_menit = models.CharField(max_length=10)
    diagnosis = models.TextField()
    intruksi = models.TextField()
    alergi = models.TextField()
    riwayat_penyakit = models.TextField()
    resep = models.TextField()
    token = models.CharField(max_length=64, blank=True, null=True)