from uuid import uuid4
from django.db import models
from .application import Application

class ChildcareType(models.Model):
    """
    Model for CHILDCARE_TYPE table
    """
    childcare_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    zero_to_five = models.BooleanField()
    five_to_eight = models.BooleanField()
    eight_plus = models.BooleanField()
    overnight_care = models.NullBooleanField()

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
            'zero_to_five',
            'five_to_eight',
            'eight_plus',
            'overnight_care'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CHILDCARE_TYPE'
