from uuid import uuid4
from django.db import models
from application.models import Application, AdultInHome


class AdultInHomeAddress(models.Model):
    """
    Model for ADULT_IN_HOME_ADDRESS table
    """
    adult_in_home_address_id = models.UUIDField(primary_key=True, default=uuid4)
    adult_id = models.ForeignKey(AdultInHome, on_delete=models.CASCADE, db_column='adult_id')
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    adult_in_home_address = models.IntegerField(blank=True, null=True)
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)

    moved_in_day = models.IntegerField(blank=True, null=True)
    moved_in_month = models.IntegerField(blank=True, null=True)
    moved_in_year = models.IntegerField(blank=True, null=True)

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
            'adult_in_home_address',
            'street_line1',
            'street_line2',
            'town',
            'county',
            'country',
            'postcode',
        )

    class Meta:
        db_table = 'ADULT_IN_HOME_ADDRESS'


    def get_moved_in_date(self):
        if not all((self.moved_in_year, self.moved_in_month, self.moved_in_day)):
            return None
        return date(self.moved_in_year, self.moved_in_month, self.moved_in_day)

    def set_moved_in_date(self, moved_in_date):
        self.moved_in_year = moved_in_date.year
        self.moved_in_month = moved_in_date.month
        self.moved_in_day = moved_in_date.day

    @classmethod
    def get_id(cls, app_id):
        adult_id = AdultInHome.get_id(app_id)
        return cls.objects.get(adult_id=adult_id)