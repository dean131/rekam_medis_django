from django.db import transaction

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from base.models import Dokter, Apoteker, Pasien, User
from .serializers import PasienModelSerializer, DokterModelSerializer, ApotekerModelSerializer, UserModelSerializer


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
        user_serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**user_serializer.validated_data)
        
        request.data.update({'user': user.id})
        pasien_serializer = PasienModelSerializer(data=request.data)
        pasien_serializer.is_valid(raise_exception=True)
        pasien = Pasien.objects.create(**pasien_serializer.validated_data)

        serializer = PasienModelSerializer(pasien)
        return Response(
            {
                'code': '201',
                'status': 'success',
                'message': 'Registrasi Berhasil.'
            }, 
            status=status.HTTP_201_CREATED
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