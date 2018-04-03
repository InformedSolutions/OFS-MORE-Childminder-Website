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

    @property
    def timelog_fields(self):
        """
        Specify which fields to track in this model once application is returned.

        Used for signals only. Check base.py for available signals.
        This is used for logging fields which gonna be updated by applicant
        once application status changed to "FURTHER_INFORMATION" on the arc side

        Returns:
            tuple of fields which needs update tracking when application is returned
        """

        return (
            'send_hdb_declare',
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'HDB'
