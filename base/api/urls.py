from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('pendaftaran', views.PendaftaranModelViewset, basename='pendaftaran')
router.register('jadwal_dokter', views.JadwalDokterModelViewset, basename='jadwal_dokter')
router.register('pemeriksaan', views.PemeriksaanModelViewset, basename='pemeriksaan')


urlpatterns = [
    path('', include(router.urls)),
]