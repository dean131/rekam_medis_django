import datetime
import os
import httpx
import asyncio
from io import BytesIO

from xhtml2pdf import pisa

from django.template.loader import get_template
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from base.models import Pendaftaran, Pemeriksaan, JadwalDokter
from account.models import Pasien, Dokter

from .serializers import (
    PendaftaranModelSerializer, 
    JadwalDokterModelSerializer,
    RiwayatPendaftaranModelSerializer,
)

from cryptography.fernet import Fernet


def render_to_pdf(context_dict):
    templates = get_template('template_pdf.html')
    html = templates.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None


class PendaftaranModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        exists = Pendaftaran.objects.filter(
            Q(Q(status='belum_bayar') | Q(status='antre')),
            pasien=request.user.pasien.id, 
            dokter=request.data['dokter'],
            tanggal=request.data['tanggal'],
        ).exists()

        if exists:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Anda sudah mendaftar pada dokter dan tanggal tersebut. Silahkan cek riwayat pendaftaran.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dokter = Dokter.objects.filter(id=request.data['dokter']).first()
        count = Pendaftaran.objects.filter(tanggal=request.data['tanggal'], dokter=dokter).count()

        if count >= dokter.max_pasien:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Antrean Penuh, coba pilih lain waktu.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Pendaftaran.objects.create(
            pasien=request.user.pasien,
            dokter=dokter,
            tanggal=request.data['tanggal'],
            asuransi=request.data['asuransi'],
            status='belum_bayar',
            no_antrean=None
        )

        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Pendaftaran berhasil dilakukan.',
            }, 
            status=status.HTTP_201_CREATED
        )
    
    def list(self, request):
        pendaftaran = Pendaftaran.objects.all()
        serializer = PendaftaranModelSerializer(pendaftaran, many=True)
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        pendaftaran = Pendaftaran.objects.filter(id=pk).first()
        serializer = RiwayatPendaftaranModelSerializer(pendaftaran, context={'request': request})

        if pendaftaran.status == 'antre':
            count = Pendaftaran.objects.filter(tanggal=pendaftaran.tanggal, status='selesai').count()
            antrean_saat_ini = (pendaftaran.no_antrean - count) - 1
            return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil diambil.',
                'antrean_saat_ini': antrean_saat_ini,
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def update(self, request, pk=None):
        pendaftaran = Pendaftaran.objects.filter(id=pk).first()
        dokter = Dokter.objects.filter(id=request.data['dokter']).first()

        if request.data['tanggal'] != pendaftaran.tanggal:
            count = Pendaftaran.objects.filter(tanggal=request.data['tanggal']).count()
            if count >= dokter.max_pasien:
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'Antrean Penuh, coba pilih lain waktu.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            pendaftaran.tanggal = request.data['tanggal']

        pendaftaran.dokter = dokter
        pendaftaran.poli = dokter.poli
        pendaftaran.asuransi = request.data['asuransi']
        pendaftaran.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil diupdate.',
            }, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        pendaftaran = Pendaftaran.objects.filter(id=pk).first()
        pendaftaran.delete()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil dihapus.',
            }, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def bayar(self, request, pk=None):
        pendaftaran = Pendaftaran.objects.get(id=pk)

        jml_pendaftaran = Pendaftaran.objects.filter(tanggal=pendaftaran.tanggal, no_antrean__isnull=False).count()

        pendaftaran.status = 'antre'
        pendaftaran.no_antrean = jml_pendaftaran + 1
        pendaftaran.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Pendaftaran berhasil dibayar.',
            }, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def riwayat(self, request):
        pasien = Pasien.objects.filter(id=request.query_params.get('pasien_id')).first()

        status_param = request.query_params.get('status')
        pendaftaran = Pendaftaran.objects.filter(pasien=pasien, status=status_param)

        serializer = PendaftaranModelSerializer(pendaftaran, many=True)
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Pendaftaran berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    

class PemeriksaanModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    async def send_wa_msg(self, number, message):
        async with httpx.AsyncClient() as client:
            res = await client.post(
                url='https://api.fonnte.com/send', 
                headers={'Authorization': 'D2Rgt2EnoYQ7G5K-wrFg'},
                json={
                    'target': number, 
                    'message': message
                }
            )
            return res

    def create(self, request):
        pendaftaran = Pendaftaran.objects.filter(id=request.data.get('pendaftaran_id')).first()

        if not pendaftaran:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Pendaftaran tidak ditemukan.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if pendaftaran.status == 'belum_bayar':
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Pasien belum membayar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        token = str(Fernet.generate_key(), 'UTF-8')

        if Pemeriksaan.objects.filter(pendaftaran=pendaftaran).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Pasien sudah diperiksa.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        Pemeriksaan.objects.create(
            pendaftaran=pendaftaran,
            path_pdf=f'{pendaftaran.id}.pdf.enc',
            token=token
        )

        pdf = render_to_pdf({
            'pasien': pendaftaran.pasien,
            'keluhan': request.data['keluhan'],
            'suhu_tubuh': request.data['suhu_tubuh'],
            'tensi_darah': request.data['tensi_darah'],
            'berat_badan': request.data['berat_badan'],
            'tinggi_badan': request.data['tinggi_badan'],
            'nadi_per_menit': request.data['nadi_per_menit'],
            'intruksi': request.data['intruksi'],
            'alergi': request.data['alergi'],
            'riwayat_penyakit': request.data['riwayat_penyakit'],
            'diagnosis': request.data['diagnosis'],
            'resep': request.data['resep'],
            'tanggal_pembuatan': datetime.date.today(),
            # 'catatan': request.data['catatan'],
        })

        fernet = Fernet(token)
        encrypted_data = fernet.encrypt(pdf.content)
        with open(f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf.enc', 'wb') as f:
            f.write(encrypted_data)

        message = f'Token anda adalah:\n\n*{token}*\n\nSilahkan masukkan token tersebut pada aplikasi untuk melihat hasil pemeriksaan.\n\n ID pendaftaran: *{pendaftaran.id}*\n\nTerima kasih.'
        # asyncio.run(self.send_wa_msg(pendaftaran.pasien.no_telp, message))

        pendaftaran.status = 'selesai'
        pendaftaran.save()
        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Pemeriksaan berhasil dilakukan.',
            }, 
            status=status.HTTP_201_CREATED, 
        )
    
    @action(detail=False, methods=['post'])
    def get_pdf(self, request):
        try:
            pendaftaran = Pendaftaran.objects.filter(id=request.data.get('pendaftaran_id')).first()
            # pemeriksaan = Pemeriksaan.objects.filter(pendaftaran=pendaftaran).first()
            key = bytes(request.data.get('key'), 'UTF-8')

            with open(f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf.enc', 'rb') as f:
                encrypted_data = f.read()

            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)

            # return HttpResponse(decrypted_data, content_type='application/pdf')

            with open(f'{settings.MEDIA_ROOT}/decrypted/{pendaftaran.id}.pdf', 'wb') as f:
                f.write(decrypted_data)

            host = request.META['HTTP_HOST']
            return Response(
                {
                    'code': '200',
                    'status': 'success',
                    'message': 'Data Pemeriksaan berhasil diambil.',
                    'data': f'{host}{settings.MEDIA_URL}decrypted/{pendaftaran.id}.pdf'
                }, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': str(e),
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )


class JadwalDokterModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        jadwal_dokter = JadwalDokter.objects.all()
        serializer = JadwalDokterModelSerializer(jadwal_dokter, many=True, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Jadwal Dokter berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )

    def create(self, request):
        dokter = Dokter.objects.get(id=request.data['dokter'])
        
        JadwalDokter.objects.create(
            dokter=dokter,
            hari=request.data['hari'],
            jam_mulai=request.data['jam_mulai'],
            jam_selesai=request.data['jam_selesai'],
        )

        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Jadwal Dokter berhasil dibuat.',
            }, 
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        jadwal_dokter = JadwalDokter.objects.filter(id=pk).first()
        jadwal_dokter.hari = request.data['hari']
        jadwal_dokter.jam_mulai = request.data['jam_mulai']
        jadwal_dokter.jam_selesai = request.data['jam_selesai']
        jadwal_dokter.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Jadwal Dokter berhasil diupdate.',
            }, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        jadwal_dokter = JadwalDokter.objects.filter(id=pk).first()
        jadwal_dokter.delete()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Jadwal Dokter berhasil dihapus.',
            }, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def dokter_tersedia(self, request):
        tanggal = request.query_params.get('tanggal').split('-')
        poli = request.query_params.get('poli')

        int_hari = datetime.date(int(tanggal[0]), int(tanggal[1]), int(tanggal[2])).weekday()
        hari = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']

        jadwal_dokter = JadwalDokter.objects.filter(hari=hari[int_hari], dokter__poli=poli)
        serializer = JadwalDokterModelSerializer(jadwal_dokter, many=True, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Jadwal Dokter berhasil diambil.',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    

class DashboardDokterViewSet(ViewSet):
    def list(self, request):
        dokter = Dokter.objects.filter(user=request.user).first()
        tanggal = datetime.date.today()

        jml_pasien_belum_bayar_hari_ini = Pendaftaran.objects.filter(dokter=dokter, status='belum_bayar', tanggal=tanggal).count()
        jml_pasien_antre_hari_ini = Pendaftaran.objects.filter(dokter=dokter, status='antre', tanggal=tanggal).count()
        jml_pasien_selesai_hari_ini = Pendaftaran.objects.filter(dokter=dokter, status='selesai', tanggal=tanggal).count()
        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Data Dashboard Dokter berhasil diambil.',
                'data': {
                    'jml_pasien_belum_bayar_hari_ini': jml_pasien_belum_bayar_hari_ini,
                    'jml_pasien_antre_hari_ini': jml_pasien_antre_hari_ini,
                    'jml_pasien_selesai_hari_ini': jml_pasien_selesai_hari_ini,
                }
            }, 
            status=status.HTTP_200_OK
        )
    