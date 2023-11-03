import datetime

from rest_framework import serializers

from account.models import Dokter, User, Pasien, Apoteker, Resepsionis

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
    umur = serializers.SerializerMethodField()

    class Meta:
        model = Pasien
        fields = '__all__'

    def get_umur(self, obj):
        today = datetime.date.today()
        born = obj.tanggal_lahir
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class DokterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dokter
        fields = '__all__'


class ApotekerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apoteker
        fields = '__all__'


class ResepsionisModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resepsionis
        fields = '__all__'