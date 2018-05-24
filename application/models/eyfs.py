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
    eyfs_course_name = models.CharField(max_length=50, blank=True, )
    eyfs_course_date_day = models.IntegerField(blank=True, null=True)
    eyfs_course_date_month = models.IntegerField(blank=True, null=True)
    eyfs_course_date_year = models.IntegerField(blank=True, null=True)

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
            'eyfs_course_name',
            'eyfs_course_date_day',
            'eyfs_course_date_month',
            'eyfs_course_date_year'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'EYFS'
