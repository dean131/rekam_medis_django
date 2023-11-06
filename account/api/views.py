from django.db import transaction

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from account.models import Dokter, Pasien, User, Resepsionis

from .serializers import (
    PasienModelSerializer, 
    DokterModelSerializer, 
    ResepsionisModelSerializer,
)


class PasienModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Pasien.objects.all()
        serializer = PasienModelSerializer(queryset, many=True, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        pasien = Pasien.objects.filter(pk=pk).first()
        serializer = PasienModelSerializer(pasien, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def update(self, request, pk=None):
        pasien = Pasien.objects.filter(pk=pk).first()
        pasien.nik = request.data['nik']
        pasien.tanggal_lahir = request.data['tanggal_lahir']
        pasien.jenis_kelamin = request.data['jenis_kelamin']
        pasien.alamat = request.data['alamat']
        pasien.no_telp = request.data['no_telp']
        pasien.pekerjaan = request.data['pekerjaan']
        pasien.save()

        user = User.objects.get(pk=pasien.user.pk)
        user.nama_lengkap = request.data['nama_lengkap']
        user.foto = request.data['foto']

        email = request.data['email']
        if email != user.email:
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'Email sudah terdaftar.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = email
        user.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Update Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        pasien = Pasien.objects.get(pk=pk)
        user = User.objects.get(pk=pasien.user.pk)
        pasien.delete()
        user.delete()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Delete Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )


class DokterModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        dokter = Dokter.objects.all()
        serializer = DokterModelSerializer(dokter, many=True, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        dokter = Dokter.objects.get(pk=pk)
        serializer = DokterModelSerializer(dokter, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        dokter = Dokter.objects.get(pk=pk)
        dokter.poli = request.data['poli']
        dokter.max_pasien = request.data['max_pasien']
        dokter.save()

        user = User.objects.get(pk=dokter.user.pk)
        user.nama_lengkap = request.data['nama_lengkap']
        user.foto = request.data['foto']

        email = request.data['email']
        if email != user.email:
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'Email sudah terdaftar.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = email
        user.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Update Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        dokter = Dokter.objects.get(pk=pk)
        user = User.objects.get(pk=dokter.user.pk)
        dokter.delete()
        user.delete()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Delete Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )


class ResepsionisModelViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        resepsionis = Resepsionis.objects.all()
        serializer = ResepsionisModelSerializer(resepsionis, many=True, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        resepsionis = Resepsionis.objects.get(pk=pk)
        serializer = ResepsionisModelSerializer(resepsionis, context={'request': request})
        return Response(
            {
                'code': '200',
                'status': 'success',
                'data': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    def update(self, request, pk=None):
        resepsionis = Resepsionis.objects.get(pk=pk)

        user = User.objects.get(pk=resepsionis.user.pk)
        user.nama_lengkap = request.data['nama_lengkap']
        user.foto = request.data['foto']

        email = request.data['email']
        if email != user.email:
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'Email sudah terdaftar.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = email
        user.save()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Update Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        resepsionis = Resepsionis.objects.get(pk=pk)
        user = User.objects.get(pk=resepsionis.user.pk)
        resepsionis.delete()
        user.delete()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Delete Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )


class RegisterViewset(ViewSet):
    permission_classes = [AllowAny]

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def pasien(self, request):
        # CEK EMAIL SUDA TERDAFTAR ATAU BELUM
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # CEK NIK SUDA TERDAFTAR ATAU BELUM
        if Pasien.objects.filter(nik=request.data['nik']).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'NIK sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )


        user = User.objects.create_user(
            email=request.data['email'], 
            password=request.data['password'],
            nama_lengkap=request.data['nama_lengkap'],
            role='pasien',
            foto=request.FILES.get('foto', None),
        )

        Pasien.objects.create(
            user=user,
            nik=request.data['nik'],
            tanggal_lahir=request.data['tanggal_lahir'],
            jenis_kelamin=request.data['jenis_kelamin'],
            alamat=request.data['alamat'],
            no_telp=request.data['no_telp'],
            pekerjaan=request.data['pekerjaan'],
        )

        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Registrasi Berhasil.'
            }, 
            status=status.HTTP_201_CREATED
        )
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def dokter(self, request):
        # CEK EMAIL SUDA TERDAFTAR ATAU BELUM
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=request.data['email'], 
            password=request.data['password'],
            nama_lengkap=request.data['nama_lengkap'],
            role='dokter',
        )

        Dokter.objects.create(
            user=user,
            poli=request.data['poli'],
            max_pasien=request.data['max_pasien'],
        )

        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Registrasi Berhasil.'
            }, 
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def resepsionis(self, request):
        # CEK EMAIL SUDA TERDAFTAR ATAU BELUM
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=request.data['email'], 
            password=request.data['password'],
            nama_lengkap=request.data['nama_lengkap'],
            role='resepsionis',
        )

        Resepsionis.objects.create(
            user=user,
        )

        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Registrasi Berhasil.'
            }, 
            status=status.HTTP_201_CREATED
        )
