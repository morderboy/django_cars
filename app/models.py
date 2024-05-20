from django.db import models
from django.contrib.auth.models import User


class Cars(models.Model):
    name = models.TextField(blank=True, null=True)
    number = models.TextField(blank=True, null=True, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False)

    class Meta:
        managed = True
        db_table = 'Cars'


class Service(models.Model):
    start_timestamp = models.IntegerField(blank=True, null=True)
    end_timestamp = models.IntegerField(blank=True, null=True)
    oil_work = models.BooleanField(blank=True, null=True)
    fluids_work = models.BooleanField(blank=True, null=True)
    filters_work = models.BooleanField(blank=True, null=True)
    brake_system_work = models.BooleanField(blank=True, null=True)
    suspension_steering_work = models.BooleanField(blank=True, null=True)
    exhaust_work = models.BooleanField(blank=True, null=True)
    tires_work = models.BooleanField(blank=True, null=True)
    lighting_work = models.BooleanField(blank=True, null=True)
    mileage = models.IntegerField(blank=True, null=True)
    car = models.ForeignKey(Cars, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Service'
