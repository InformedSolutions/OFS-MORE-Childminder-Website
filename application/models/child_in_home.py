from uuid import uuid4
from django.db import models
from .application import Application

class ChildInHome(models.Model):
    """
    Model for CHILD_IN_HOME table
    """
    child_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    child = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CHILD_IN_HOME'
