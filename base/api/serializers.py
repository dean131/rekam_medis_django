from rest_framework import serializers

from base.models import Pendaftaran, Pemeriksaan, JadwalDokter


class PendaftaranModelSerializer(serializers.ModelSerializer):
    poli = serializers.SerializerMethodField('get_poli')
    class Meta:
        model = Pendaftaran
        fields = '__all__'

    def get_poli(self, obj):
        return obj.dokter.poli


class PemeriksaanModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pemeriksaan
        fields = '__all__'


class JadwalDokterModelSerializer(serializers.ModelSerializer):
    dokter_id = serializers.SerializerMethodField('get_dokter_id')
    nama_dokter = serializers.SerializerMethodField('get_nama_dokter')
    class Meta:
        model = JadwalDokter
        fields = ['id', 'dokter_id', 'nama_dokter', 'hari', 'jam_mulai', 'jam_selesai']

    def get_dokter_id(self, obj):
        return obj.dokter.id
    
    def get_nama_dokter(self, obj):
        return obj.dokter.user.nama_lengkap