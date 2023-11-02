from django.contrib import admin

from .models import Pemeriksaan, Pendaftaran, JadwalDokter

admin.site.register(Pemeriksaan)
admin.site.register(Pendaftaran)
admin.site.register(JadwalDokter)

admin.site.site_header = 'Rekam Medis'
admin.site.site_title = 'Rekam Medis'
admin.site.index_title = 'Rekam Medis'
