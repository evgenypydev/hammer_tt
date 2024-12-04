import re

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import CharField, ValidationError, Serializer, ModelSerializer

from .models import User


class PhoneNumberFieldSerializer(CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        phone_regex = re.compile(r'^\+?\d{10,15}$')
        if not phone_regex.match(data):
            raise ValidationError("Неверный формат номера телефона.")
        return data


class GenerateCodeSerializer(Serializer):
    phone_number = PhoneNumberFieldSerializer()


class VerifyCodeSerializer(Serializer):
    phone_number = PhoneNumberFieldSerializer()
    code = CharField(max_length=4)


class UserProfileSerializer(ModelSerializer):
    invited_users = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'phone_number',
            'invite_code',
            'activated_invite_code',
            'invited_users',
        ]

    def get_invited_users(self, obj):
        users = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone_number for user in users]


class ActivateInviteCodeSerializer(Serializer):
    invite_code = CharField(max_length=6)