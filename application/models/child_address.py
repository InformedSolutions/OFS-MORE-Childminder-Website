from uuid import uuid4
from django.db import models
from .application import Application


class ChildAddress(models.Model):
    """
    Model for CHILD_OUTSIDE_HOME_ADDRESS table
    """
    child_address_id = models.UUIDField(primary_key=True, default=uuid4)
    child = models.IntegerField(null=True, blank=True)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE,
                                       db_column='application_id')
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)

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
            'street_line1',
            'street_line2',
            'town',
            'county',
            'country',
            'postcode',
        )

    class Meta:
        db_table = 'CHILD_ADDRESS'
