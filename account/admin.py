from django.contrib import admin

from base.models import User, Dokter, Pasien, Apoteker

admin.site.register(User)
admin.site.register(Dokter)
admin.site.register(Pasien)
admin.site.register(Apoteker)