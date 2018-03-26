from uuid import uuid4
from django.db import models
from .application import Application

class EYFS(models.Model):
    """
    Model for EYFS table
    """
    eyfs_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    eyfs_understand = models.NullBooleanField(blank=True, null=True, default=None)
    eyfs_training_declare = models.NullBooleanField(blank=True, null=True, default=None)
    share_info_declare = models.NullBooleanField(blank=True, null=True, default=None)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'EYFS'
