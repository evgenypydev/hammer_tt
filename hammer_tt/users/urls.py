from django.urls import path

from .endpoints import GenerateCodeAPIView, VerifyCodeAPIView, UserProfileAPIView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('generate_code/', GenerateCodeAPIView.as_view(), name='generate_code'),
    path('verify_code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]