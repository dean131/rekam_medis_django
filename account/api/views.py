from django.db import transaction
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken

from account.models import Dokter, Pasien, User, Resepsionis

from .serializers import (
    PasienModelSerializer, 
    DokterModelSerializer, 
    ResepsionisModelSerializer,
    UserModelSerializer,
)

from django.contrib.auth import login, logout


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
        
        if pasien.user.email != request.data.get('email'):
            if User.objects.filter(email=request.data.get('email')).exists():
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'Email sudah terdaftar.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if pasien.nik != request.data.get('nik'):
            if Pasien.objects.filter(nik=request.data.get('nik')).exists():
                return Response(
                    {
                        'code': '400',
                        'status': 'failed',
                        'message': 'NIK sudah terdaftar.',
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if request.data.get('nik'): pasien.nik = request.data.get('nik') 
        if request.data.get('tanggal_lahir'): pasien.tanggal_lahir = request.data.get('tanggal_lahir')
        if request.data.get('jenis_kelamin'): pasien.jenis_kelamin = request.data.get('jenis_kelamin')
        if request.data.get('alamat'): pasien.alamat = request.data.get('alamat')
        if request.data.get('no_telp'): pasien.no_telp = request.data.get('no_telp')
        if request.data.get('pekerjaan'): pasien.pekerjaan = request.data.get('pekerjaan')
        pasien.save()

        user = User.objects.get(pk=pasien.user.pk)
        if request.data.get('nama_lengkap'): user.nama_lengkap = request.data.get('nama_lengkap') 
        if request.data.get('foto'): user.foto = request.data.get('foto', None)

        email = request.data.get('email')
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
        dokter.poli = request.data.get('poli')
        dokter.max_pasien = request.data.get('max_pasien')
        dokter.save()

        user = User.objects.get(pk=dokter.user.pk)
        user.nama_lengkap = request.data.get('nama_lengkap')
        user.foto = request.data.get('foto', None)

        email = request.data.get('email')
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
        user.nama_lengkap = request.data.get('nama_lengkap')
        user.foto = request.data.get('foto', None)

        email = request.data.get('email')
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




class UserLoginViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        print(user)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            refresh['user'] = UserModelSerializer(user).data
            
            if user.role == 'pasien':
                pasien = Pasien.objects.get(user=user)
                pasien = PasienModelSerializer(pasien).data
                refresh['pasien_id'] = pasien['id']
                refresh['nik'] = pasien['nik']
                refresh['tanggal_lahir'] = pasien['tanggal_lahir']
                refresh['no_telp'] = pasien['no_telp']
                refresh['jenis_kelamin'] = pasien['jenis_kelamin']
                refresh['pekerjaan'] = pasien['pekerjaan']
                refresh['alamat'] = pasien['alamat']
            
            return Response({
                'code': '200',
                'status': 'success',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': '400',
                'status': 'failed',
                'message': 'email atau password tidak valid',
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterViewset(ViewSet):
    permission_classes = [AllowAny]

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def pasien(self, request):
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Pasien.objects.filter(nik=request.data.get('nik')).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'NIK sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )


        user = User.objects.create_user(
            email=request.data.get('email'), 
            password=request.data.get('password'),
            nama_lengkap=request.data.get('nama_lengkap'),
            role='pasien',
            foto=request.data.get('foto', None),
        )

        Pasien.objects.create(
            user=user,
            nik=request.data.get('nik'),
            tanggal_lahir=request.data.get('tanggal_lahir'),
            jenis_kelamin=request.data.get('jenis_kelamin'),
            alamat=request.data.get('alamat'),
            no_telp=request.data.get('no_telp'),
            pekerjaan=request.data.get('pekerjaan'),
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
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=request.data.get('email'), 
            password=request.data.get('password'),
            nama_lengkap=request.data.get('nama_lengkap'),
            role='dokter',
            foto=request.data.get('foto', None),
        )

        Dokter.objects.create(
            user=user,
            poli=request.data.get('poli'),
            max_pasien=request.data.get('max_pasien'),
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
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response(
                {
                    'code': '400',
                    'status': 'failed',
                    'message': 'Email sudah terdaftar.',
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=request.data.get('email'), 
            password=request.data.get('password'),
            nama_lengkap=request.data.get('nama_lengkap'),
            role='resepsionis',
            foto=request.data.get('foto', None),
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


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {
                'code': '200',
                'status': 'success',
                'message': 'Logout Berhasil.'
            }, 
            status=status.HTTP_200_OK
        )