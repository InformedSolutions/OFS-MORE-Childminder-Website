from uuid import uuid4
from django.db import models
from .application import Application

class ApplicantPersonalDetails(models.Model):
    """
    Model for APPLICANT_PERSONAL_DETAILS table
    """
    personal_detail_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    birth_day = models.IntegerField(blank=True, null=True)
    birth_month = models.IntegerField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'APPLICANT_PERSONAL_DETAILS'
