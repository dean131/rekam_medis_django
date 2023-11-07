from django.contrib import admin

from .models import User, Dokter, Pasien, Resepsionis

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nama_lengkap', 'role', 'foto', 'is_admin')
    search_fields = ('email', 'nama_lengkap')
    

class DokterAdmin(admin.ModelAdmin):
    list_display = ('id', 'user' , 'poli')


class PasienAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tanggal_lahir', 'jenis_kelamin', 'alamat')


class ResepsionisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


admin.site.register(Resepsionis, ResepsionisAdmin)
admin.site.register(Dokter, DokterAdmin)
admin.site.register(Pasien, PasienAdmin)
admin.site.register(User, UserAdmin)