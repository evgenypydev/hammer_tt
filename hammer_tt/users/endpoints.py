import random
import time

from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from .models import User
from .serializers import GenerateCodeSerializer, VerifyCodeSerializer, UserProfileSerializer, \
    ActivateInviteCodeSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse


class GenerateCodeAPIView(APIView):
    @extend_schema(
        request=GenerateCodeSerializer,
        responses={
            200: OpenApiResponse(
                response=Serializer,
                description='Код подтверждения сгенерирован.',
                examples=[
                    {
                        'message': 'Код подтверждения сгенерирован.',
                        'code': '1234'
                    }
                ]
            ),
            400: OpenApiResponse(
                response=Serializer,
                description='Ошибка валидации.',
                examples=[
                    {
                        'phone_number': ['Неверный формат номера телефона.']
                    }
                ]
            ),
        },
        description='Генерирует 4-значный код подтверждения для указанного номера телефона.',
    )
    def post(self, request):
        serializer = GenerateCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            time.sleep(2)
            code = '{:04d}'.format(random.randint(0, 9999))
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': phone_number,
                    'password': make_password(None)
                }
            )
            user.verification_code = code
            user.save()
            return Response({
                'message': 'Код подтверждения сгенерирован.',
                'code': code
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeAPIView(APIView):
    @extend_schema(
        request=VerifyCodeSerializer,
        responses={
            200: OpenApiResponse(
                response=Serializer,
                description='Верификация успешна.',
                examples=[
                    {
                        'message': 'Верификация успешна.',
                        'refresh': '<refresh_token>',
                        'access': '<access_token>',
                    }
                ]
            ),
            400: OpenApiResponse(
                response=Serializer,
                description='Ошибка верификации.',
                examples=[
                    {
                        'error': 'Неверный код подтверждения.'
                    }
                ]
            ),
        },
        description='Верифицирует код подтверждения и аутентифицирует пользователя.',
    )
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return Response({'error': 'Пользователь с таким номером не найден.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.verification_code == code:
                user.verification_code = None
                user.save()

                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'Верификация успешна.',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неверный код подтверждения.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(
        responses={
            200: UserProfileSerializer,
        },
        description='Возвращает профиль пользователя, включая инвайт-коды.',
    )
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ActivateInviteCodeSerializer,
        responses={
            200: OpenApiResponse(
                response=ActivateInviteCodeSerializer,
                description='Инвайт-код успешно активирован.'
            ),
            400: OpenApiResponse(
                response=ActivateInviteCodeSerializer,
                description='Ошибка активации инвайт-кода.'
            ),
        },
        description='Активирует инвайт-код другого пользователя.',
    )
    def post(self, request):
        serializer = ActivateInviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.activated_invite_code:
                return Response({'error': 'Инвайт-код уже был активирован ранее.'}, status=status.HTTP_400_BAD_REQUEST)
            invite_code = serializer.validated_data['invite_code']
            if User.objects.filter(invite_code=invite_code).exists():
                user.activated_invite_code = invite_code
                user.save()
                return Response({'message': 'Инвайт-код успешно активирован.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Инвайт-код не найден.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)