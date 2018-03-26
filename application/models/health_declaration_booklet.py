from uuid import uuid4
from django.db import models
from .application import Application

class HealthDeclarationBooklet(models.Model):
    """
    Model for HEALTH_DECLARATION_BOOKLET table
    """
    hdb_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    send_hdb_declare = models.NullBooleanField(blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'HDB'
