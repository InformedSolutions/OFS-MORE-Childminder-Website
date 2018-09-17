from django.db import models
from .childbase import ChildBase


class ChildInHome(ChildBase):
    """
    Model for CHILD_IN_HOME table
    """
    relationship = models.CharField(max_length=100, blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

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
            'child',
            'first_name',
            'middle_names',
            'last_name',
            'birth_day',
            'birth_month',
            'birth_year',
            'relationship'
        )

    class Meta:
        db_table = 'CHILD_IN_HOME'
