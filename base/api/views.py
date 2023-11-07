import datetime
import os
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
)

from cryptography.fernet import Fernet


def encrypt_file(filename, output_file, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as f:
        file_data = f.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(output_file, 'wb') as f:
        f.write(encrypted_data)


def decrypt_file(filename, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as f:
        encrypted_data = f.read()
    return fernet.decrypt(encrypted_data)


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
        serializer = PendaftaranModelSerializer(pendaftaran)

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

    @action(detail=True, methods=['get'])
    def riwayat(self, request, pk=None):
        pasien = Pasien.objects.filter(id=pk).first()

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

    def create(self, request):
        pendaftaran = Pendaftaran.objects.filter(
            pasien=request.user.pasien.id,
        ).first()

        if not pendaftaran:
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Pasien belum mendaftar.',
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

        pdf = render_to_pdf({
            'pasien': request.user.pasien,
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


        with open(f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf', 'wb') as f:
            f.write(pdf.content)

        encrypt_file(
            f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf', 
            f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf.enc', 
            token
        )
        
        os.remove(f'{settings.MEDIA_ROOT}/{pendaftaran.id}.pdf')

        pemeriksaan = Pemeriksaan.objects.filter(pendaftaran=pendaftaran)
        if not pemeriksaan:
            Pemeriksaan.objects.create(
                pendaftaran=pendaftaran,
                path_pdf=f'{pendaftaran.id}.pdf.enc',
                token=token
            )

        pemeriksaan.update(
            path_pdf=f'{pendaftaran.id}.pdf.enc',
            token=token
        )   

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
    
    def retrieve(self, request, pk=None):
        pemeriksaan = Pemeriksaan.objects.get(id=pk)

        user_key = request.data['key']
        key = bytes(user_key, 'UTF-8')
        decrypted_data = decrypt_file(f'{settings.MEDIA_ROOT}/{pemeriksaan.path_pdf}', key)
        return HttpResponse(decrypted_data, content_type='application/pdf')


class JadwalDokterModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

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
    


    