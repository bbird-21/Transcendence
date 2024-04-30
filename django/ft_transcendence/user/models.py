from django.db import models
from django.contrib.auth.models import User
import uuid


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ft_uuid = models.CharField(max_length=42)
    pseudo = models.CharField(max_length=21)


# Create your models here.
