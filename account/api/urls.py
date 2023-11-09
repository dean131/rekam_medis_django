from django.urls import path, include

from rest_framework import routers

from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)

from . import views


router = routers.DefaultRouter()
router.register('register', views.RegisterViewset, basename='register')
router.register('dokter', views.DokterModelViewset, basename='dokter')
router.register('pasien', views.PasienModelViewset, basename='pasien')
router.register('resepsionis', views.ResepsionisModelViewset, basename='resepsionis')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserLoginViewSet.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]