from django.db import models
from users.models import Seller


class Shop(models.Model):
    owner = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='owner')
    name = models.CharField(max_length=250)
    image = models.URLField(max_length=250, default="https://ibb.co.com/jZhrJtTS")
    description = models.TextField()
    location = models.CharField(max_length=250)
    hotline = models.CharField(max_length=20, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.name}"
