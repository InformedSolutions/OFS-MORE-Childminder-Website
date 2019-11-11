from uuid import uuid4
from django.db import models
from .application import Application

class ChildcareTiming(models.Model):
    """
    Model for CHILDCARE_TYPE table
    """
    childcare_timing_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    weekday_before_school = models.BooleanField()
    weekday_after_school = models.BooleanField()
    weekday_am = models.BooleanField()
    weekday_pm = models.BooleanField()
    weekday_all_day = models.BooleanField()
    weekend_am = models.BooleanField()
    weekend_pm = models.BooleanField()
    weekend_all_day = models.BooleanField()

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
            'weekday_before_school',
            'weekday_after_school',
            'weekday_am',
            'weekday_pm',
            'weekday_all_day',
            'weekend_am',
            'weekend_pm',
            'weekend_all_day'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CHILDCARE_TIMING'
