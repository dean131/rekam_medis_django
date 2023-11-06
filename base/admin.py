from django.contrib import admin

from .models import Pemeriksaan, Pendaftaran, JadwalDokter


class PemeriksaanAdmin(admin.ModelAdmin):
    list_display = ('id', 'pendaftaran', 'path_pdf', 'token')
    search_fields = ('pendaftaran__pasien__user__nama_lengkap', 'pendaftaran__dokter__user__nama_lengkap')

admin.site.register(Pemeriksaan, PemeriksaanAdmin)


class PendafaranAdmin(admin.ModelAdmin):
    list_display = ('id', 'pasien', 'dokter', 'poli', 'asuransi', 'status', 'tanggal', 'no_antrean')
    list_filter = ('status', 'tanggal')
    search_fields = ('pasien__user__nama_lengkap', 'dokter__user__nama_lengkap', 'poli')

admin.site.register(Pendaftaran, PendafaranAdmin)

admin.site.register(JadwalDokter)

admin.site.site_header = 'Rekam Medis'
admin.site.site_title = 'Rekam Medis'
admin.site.index_title = 'Rekam Medis'
