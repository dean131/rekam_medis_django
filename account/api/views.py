from django.db import transaction

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from base.models import Dokter, Apoteker, Pasien, User
from .serializers import (
    PasienModelSerializer, 
    DokterModelSerializer, 
    ApotekerModelSerializer, 
    UserModelSerializer,
    ResepsionisModelSerializer,
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

        request.data.update({'role': 'pasien'})
        user_serializer = UserModelSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()

            request.data.update({'user': user.id})
            pasien_serialzer = PasienModelSerializer(data=request.data)
            if pasien_serialzer.is_valid(raise_exception=True):
                pasien_serialzer.save()

                return Response(
                    {
                        'code': '201',
                        'status': 'success',
                        'message': 'Registrasi Berhasil.'
                    }, 
                    status=status.HTTP_201_CREATED
                )
        
        return Response(
            {
                'code': '400',
                'status': 'failed',
                'message': 'Registrasi Gagal.'
            }, 
            status=status.HTTP_400_BAD_REQUEST
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

        request.data.update({'role': 'dokter'})
        user_serializer = UserModelSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()

            request.data.update({'user': user.id})
            dokter_serialzer = DokterModelSerializer(data=request.data)
            if dokter_serialzer.is_valid(raise_exception=True):
                dokter_serialzer.save()

                return Response(
                    {
                        'code': '201',
                        'status': 'success',
                        'message': 'Registrasi Berhasil.'
                    }, 
                    status=status.HTTP_201_CREATED
                )
            
        return Response(
            {
                'code': '400',
                'status': 'failed',
                'message': 'Registrasi Gagal.'
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def apoteker(self, request):
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

        request.data.update({'role': 'apoteker'})
        user_serializer = UserModelSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()

            request.data.update({'user': user.id})
            apoteker_serialzer = ApotekerModelSerializer(data=request.data)
            if apoteker_serialzer.is_valid(raise_exception=True):
                apoteker_serialzer.save()

                return Response(
                    {
                        'code': '201',
                        'status': 'success',
                        'message': 'Registrasi Berhasil.'
                    }, 
                    status=status.HTTP_201_CREATED
                )
            
        return Response(
            {
                'code': '400',
                'status': 'failed',
                'message': 'Registrasi Gagal.'
            }, 
            status=status.HTTP_400_BAD_REQUEST
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

        request.data.update({'role': 'resepsionis'})
        user_serializer = UserModelSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()

            request.data.update({'user': user.id})
            resepsionis_serialzer = ResepsionisModelSerializer(data=request.data)
            if resepsionis_serialzer.is_valid(raise_exception=True):
                resepsionis_serialzer.save()

                return Response(
                    {
                        'code': '201',
                        'status': 'success',
                        'message': 'Registrasi Berhasil.'
                    }, 
                    status=status.HTTP_201_CREATED
                )
            
        return Response(
            {
                'code': '400',
                'status': 'failed',
                'message': 'Registrasi Gagal.'
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )


class PasienModelViewset(ModelViewSet):
    queryset = Pasien.objects.filter()
    serializer_class = PasienModelSerializer
    permission_classes = [IsAuthenticated]


class DokterModelViewset(ModelViewSet):
    queryset = Dokter.objects.all()
    serializer_class = DokterModelSerializer


class ApotekerModelViewset(ModelViewSet):
    queryset = Apoteker.objects.filter()
    serializer_class = ApotekerModelSerializer