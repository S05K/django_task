from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    is_authorized = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, null=True)
    address = models.JSONField(default=dict)
    gst_number = models.CharField(max_length=255,null=True)


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
