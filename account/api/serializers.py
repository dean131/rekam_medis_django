from rest_framework import serializers

from base.models import Dokter, User, Pasien, Apoteker

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['nama_lengkap'] = user.nama_lengkap
        token['email'] = user.email
        token['role'] = user.role
        token['is_admin'] = user.is_admin
        # ...

        if user.role == 'pasien':
            pasien = Pasien.objects.get(user=user)
            token['pasien'] = PasienModelSerializer(pasien).data

        return token
    

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PasienModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pasien
        exclude = ['id', 'user']


class DokterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dokter
        fields = '__all__'


class ApotekerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apoteker
        fields = '__all__'