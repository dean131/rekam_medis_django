import datetime

from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from base.models import Pendaftaran, Pemeriksaan, JadwalDokter
from account.models import Dokter, Apoteker, Pasien

from .serializers import (
    PendaftaranModelSerializer, 
    JadwalDokterModelSerializer, 
    PemeriksaanModelSerializer
)


class PendaftaranModelViewset(ModelViewSet):
    queryset = Pendaftaran.objects.all()
    serializer_class = PendaftaranModelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        exists = Pendaftaran.objects.filter(
            Q(Q(status='belum_bayar') | Q(status='antre')),
            pasien=request.user.pasien.id, 
            dokter=request.data['dokter'],
        ).exists()

        if exists:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Anda sudah mendaftar pada dokter ini. Silahkan selesaikan dulu.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data.update({'pasien': request.user.pasien.id})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Pendaftaran berhasil dilakukan.',
            }, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )


class JadwalDokterModelViewset(ModelViewSet):
    queryset = Pendaftaran.objects.all()
    serializer_class = JadwalDokterModelSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def dokter_tersedia(self, request):
        tanggal = request.data['tanggal'].split('-')

        int_hari = datetime.date(int(tanggal[0]), int(tanggal[1]), int(tanggal[2])).weekday()
        hari = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']

        jadwal_dokter = JadwalDokter.objects.filter(hari=hari[int_hari])
        serializer = JadwalDokterModelSerializer(jadwal_dokter, many=True)
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Jadwal Dokter berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )