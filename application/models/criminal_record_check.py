from uuid import uuid4
from django.db import models
from .application import Application

class CriminalRecordCheck(models.Model):
    """
    Model for CRIMINAL_RECORD_CHECK table
    """
    criminal_record_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    cautions_convictions = models.BooleanField(blank=True)
    send_certificate_declare = models.NullBooleanField(blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CRIMINAL_RECORD_CHECK'
