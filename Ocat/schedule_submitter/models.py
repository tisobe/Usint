from django.db import models

# Create your models here.


class Schedule(models.Model):

    start        = models.PositiveIntegerField()
    finish       = models.PositiveIntegerField()
    contact      = models.CharField(max_length=10, blank=True)
    start_month  = models.CharField(max_length=10)
    start_day    = models.CharField(max_length=10)
    start_year   = models.CharField(max_length=10)
    finish_month = models.CharField(max_length=10)
    finish_day   = models.CharField(max_length=10)
    finish_year  = models.CharField(max_length=10)
    assigned     = models.CharField(max_length=10, blank=True)

    def __unicode__(self):
        return self.contact


