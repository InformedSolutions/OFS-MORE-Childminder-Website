from uuid import uuid4
from django.db import models
from .application import Application

class FirstAidTraining(models.Model):
    """
    Model for FIRST_AID_TRAINING table
    """
    first_aid_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    training_organisation = models.CharField(max_length=100)
    course_title = models.CharField(max_length=100)
    course_day = models.IntegerField()
    course_month = models.IntegerField()
    course_year = models.IntegerField()
    show_certificate = models.NullBooleanField(blank=True, null=True, default=None)
    renew_certificate = models.NullBooleanField(blank=True, null=True, default=None)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'FIRST_AID_TRAINING'
