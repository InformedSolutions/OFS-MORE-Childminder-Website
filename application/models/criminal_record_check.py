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
    cautions_convictions = models.NullBooleanField(blank=True)
    lived_abroad = models.NullBooleanField(blank=True)
    military_base = models.NullBooleanField(blank=True)
    capita = models.NullBooleanField(blank=True)                # dbs found on the capita list?
    enhanced_check = models.NullBooleanField(blank=True)        # stated they have a capita dbs?
    on_update = models.NullBooleanField(blank=True)             # stated they are signed up to dbs update service?
    certificate_information = models.TextField(blank=True)      # information from dbs certificate
    within_three_months = models.NullBooleanField(blank=True)   # dbs was issued within three months of lookup?

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
            'dbs_certificate_number',
            'cautions_convictions'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CRIMINAL_RECORD_CHECK'
