from django.contrib import admin

from .models import User, Dokter, Pasien, Resepsionis

admin.site.register(User)

admin.site.register(Dokter)

admin.site.register(Pasien)

admin.site.register(Resepsionis)