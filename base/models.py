from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nama_lengkap, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            nama_lengkap=nama_lengkap,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nama_lengkap, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            nama_lengkap=nama_lengkap,
            **extra_fields,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("pasien", "Pasien"),
        ("dokter", "Dokter"),
        ("apoteker", "Apoteker"),
        ("resepsionis", "Resepsionis"),
        ("admin", "Admin"),
    )

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    nama_lengkap = models.CharField(max_length=255)

    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nama_lengkap"]

    def __str__(self):
        return self.nama_lengkap

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class Pasien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nik = models.CharField(max_length=20)
    tanggal_lahir = models.DateField()
    no_telp = models.CharField(max_length=15)
    jenis_kelamin = models.CharField(max_length=10)
    pekerjaan = models.CharField(max_length=50)
    alamat = models.TextField()

    def __str__(self):
        return self.user.nama_lengkap


class Dokter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    poli = models.CharField(max_length=50)

    def __str__(self):
        return self.user.nama_lengkap


class Apoteker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.nama_lengkap
    

class Resepsionis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.nama_lengkap


class JadwalDokter(models.Model):
    dokter = models.ForeignKey(Dokter, on_delete=models.CASCADE)
    hari = models.CharField(max_length=10)
    waktu = models.CharField(max_length=10)


class Pendaftaran(models.Model):
    STATUS_CHOICES = (
        ("menunggu", "Menunggu"),
        ("proses", "Proses"),
        ("selesai", "Selesai"),
    )

    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    dokter = models.ForeignKey(Dokter, on_delete=models.CASCADE)
    tanggal = models.DateField()
    waktu = models.CharField(max_length=10)
    poli = models.CharField(max_length=50)
    asuransi = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default="menunggu")


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
    otp = models.CharField(max_length=6)