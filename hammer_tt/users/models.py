from django.contrib.auth.models import AbstractUser
from django.db import models
import string
import random

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    verification_code = models.CharField(max_length=4, blank=True, null=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)

    def generate_invite_code(self):
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            if not User.objects.filter(invite_code=code).exists():
                return code

