from django.db                  import models
from django.contrib.auth.models import User

# Create your models here.

class Usint(models.Model):

    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    #username = models.CharField(max_length=100, blank=True)
    status   = models.CharField(max_length=100, blank=True)
