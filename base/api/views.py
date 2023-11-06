import datetime
import os

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
    PemeriksaanModelSerializer
)

from cryptography.fernet import Fernet
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(context_dict):
    templates = get_template('template_pdf.html')
    html = templates.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None

# Encrypt a file
def encrypt_file(filename, output_file, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(output_file, 'wb') as file:
        file.write(encrypted_data)

# Decrypt a file
def decrypt_file(filename, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(filename, 'wb') as file:
        file.write(decrypted_data)


class PendaftaranModelViewset(ViewSet):
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
        
        dokter = Dokter.objects.filter(id=request.data['dokter']).first()
        pendaftaran = Pendaftaran.objects.filter(tanggal=request.data['tanggal'])

        if len(pendaftaran) >= dokter.max_pasien:
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
            poli=request.data['poli'],
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
        pendaftaran.pasien = request.data['pasien']
        pendaftaran.dokter = request.data['dokter']
        pendaftaran.tanggal = request.data['tanggal']
        pendaftaran.poli = request.data['poli']
        pendaftaran.asuransi = request.data['asuransi']
        pendaftaran.status = request.data['status']
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

        jml_pendaftaran = len(Pendaftaran.objects.filter(tanggal=pendaftaran.tanggal, no_antrean__isnull=False))

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
    def belum_bayar(self, request, pk=None):
        pasien = Pasien.objects.filter(id=pk).first()
        pendaftaran = Pendaftaran.objects.filter(pasien=pasien, status='belum_bayar')
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
    
    @action(detail=True, methods=['get'])
    def antre(self, request, pk=None):
        pasien = Pasien.objects.filter(id=pk).first()
        pendaftaran = Pendaftaran.objects.filter(pasien=pasien, status='antre')
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
    
    @action(detail=True, methods=['get'])
    def selesai(self, request, pk=None):
        pasien = Pasien.objects.filter(id=pk).first()
        pendaftaran = Pendaftaran.objects.filter(pasien=pasien, status='selesai')
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

        token = Fernet.generate_key()

        pdf = render_to_pdf({
            'pasien': request.user.pasien,

            # 'keluhan': request.data['keluhan'],
            # 'suhu_tubuh': request.data['suhu_tubuh'],
            # 'tensi_darah': request.data['tensi_darah'],
            # 'berat_badan': request.data['berat_badan'],
            # 'tinggi_badan': request.data['tinggi_badan'],
            # 'nadi_per_menit': request.data['nadi_per_menit'],
            # 'intruksi': request.data['intruksi'],
            # 'alergi': request.data['alergi'],
            # 'riwayat_penyakit': request.data['riwayat_penyakit'],
            # 'diagnosis': request.data['diagnosis'],
            # 'resep': request.data['resep'],
        })

        with open(settings.MEDIA_ROOT / f'generated_pdf/{pendaftaran.id}.pdf', 'wb') as f:
            f.write(pdf.content)

        encrypt_file(
            settings.MEDIA_ROOT / f'generated_pdf/{pendaftaran.id}.pdf', 
            settings.MEDIA_ROOT / f'encrypted_pdf/{pendaftaran.id}.pdf.enc', 
            token
        )
        
        os.remove(settings.MEDIA_ROOT / f'generated_pdf/{pendaftaran.id}.pdf')

        Pemeriksaan.objects.update_or_create(
            pendaftaran=pendaftaran,
            path_pdf=f'encrypted_pdf/{pendaftaran.id}.pdf.enc',
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

        print(pemeriksaan.token)
        print(type(pemeriksaan.token))

        fernet = Fernet(pemeriksaan.token)
        with open(settings.MEDIA_ROOT / pemeriksaan.path_pdf, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)

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

    @action(detail=False, methods=['post'])
    def dokter_tersedia(self, request):
        tanggal = request.data['tanggal'].split('-')

        int_hari = datetime.date(int(tanggal[0]), int(tanggal[1]), int(tanggal[2])).weekday()
        hari = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']

        jadwal_dokter = JadwalDokter.objects.filter(hari=hari[int_hari], dokter__poli=request.data['poli'])
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