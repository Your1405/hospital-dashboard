from django.db import models
from .choices import STATES

# Create your models here.
class Type(models.Model):
    type = models.CharField(max_length=32)

class State(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=128)

class Facility(models.Model):
    name = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

class Rating(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    overall = models.CharField(max_length=16)
    mortality = models.CharField(max_length=16)
    safety = models.CharField(max_length=16)
    readmission = models.CharField(max_length=16)
    experience = models.CharField(max_length=16)
    effectiveness = models.CharField(max_length=16)
    timeliness = models.CharField(max_length=16)
    imaging =  models.CharField(max_length=16)

class Procedure(models.Model):
    name = models.CharField(max_length=64)

class FacilityProcedure(models.Model):
    facility_procedure_id = models.AutoField(primary_key=True)
    facility_id = models.ForeignKey(Facility, models.CASCADE)
    procedure_id = models.ForeignKey(Procedure, models.CASCADE)
    cost = models.IntegerField()
    quality = models.CharField(max_length=16)
    value = models.CharField(max_length=16)

    class Meta: 
        managed = True
        db_table = 'dashboard_facility_procedure'
        unique_together = (('facility_id', 'procedure_id'),)