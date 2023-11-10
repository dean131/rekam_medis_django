import datetime

from rest_framework import serializers

from account.api.serializers import UserModelSerializer
from account.models import User

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
    poli = serializers.SerializerMethodField('get_poli')
    foto = serializers.SerializerMethodField('get_foto')
    is_full = serializers.SerializerMethodField('get_is_full')

    class Meta:
        model = JadwalDokter
        fields = ['id', 'dokter_id', 'nama_dokter', 'poli', 'hari', 'jam_mulai', 'jam_selesai', 'is_full', 'foto']

    def get_dokter_id(self, obj):
        return obj.dokter.id

    def get_nama_dokter(self, obj):
        return obj.dokter.user.nama_lengkap

    def get_poli(self, obj):
        return obj.dokter.poli

    def get_foto(self, obj):
        user = User.objects.get(id=obj.dokter.user.id)
        serializers = UserModelSerializer(user, context={'request': self.context['request']}).data
        if serializers['foto']:
            return serializers['foto']
        return None
    
    def get_is_full(self, obj):
        count = Pendaftaran.objects.filter(tanggal=self.context['request'].query_params.get('tanggal'), dokter=obj.dokter).count()
        if count >= obj.dokter.max_pasien:
            return True
        return False
    
    