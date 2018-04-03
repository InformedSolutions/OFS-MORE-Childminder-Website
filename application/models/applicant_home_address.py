from uuid import uuid4
from django.db import models
from .applicant_personal_details import ApplicantPersonalDetails
from .application import Application


class ApplicantHomeAddress(models.Model):
    """
    Model for APPLICANT_HOME_ADDRESS table
    """
    home_address_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE,
                                       db_column='application_id')
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    childcare_address = models.NullBooleanField(blank=True, null=True, default=None)
    current_address = models.NullBooleanField(blank=True, null=True, default=None)
    move_in_month = models.IntegerField(blank=True)
    move_in_year = models.IntegerField(blank=True)

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
            'childcare_address',
            'current_address',
            'move_in_month',
            'move_in_year'
        )


    @classmethod
    def get_id(cls, app_id):
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id)
        return cls.objects.get(personal_detail_id=personal_detail_id)

    class Meta:
        db_table = 'APPLICANT_HOME_ADDRESS'
