from datetime import datetime, date
from uuid import uuid4

from django.db import models

from .application import Application


class AdultInHome(models.Model):
    """
    Model for ADULT_IN_HOME table
    """
    adult_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(
        Application, on_delete=models.CASCADE, db_column='application_id')
    adult = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    other_title = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)

    relationship = models.CharField(max_length=100, blank=True)
    cygnum_relationship_to_childminder = models.CharField(max_length=100, blank=True)

    email = models.CharField(max_length=100, blank=True, null=True)
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    validated = models.BooleanField(default=False)
    current_treatment = models.NullBooleanField(null=True)
    serious_illness = models.NullBooleanField(null=True)
    known_to_council = models.NullBooleanField(null=True)
    reasons_known_to_council_health_check = models.TextField(default='', null=True)
    hospital_admission = models.NullBooleanField(null=True)
    health_check_status = models.CharField(max_length=50, default='To do')
    email_resent = models.IntegerField(default=0)
    email_resent_timestamp = models.DateTimeField(null=True, blank=True)
    lived_abroad = models.NullBooleanField(blank=True)
    military_base = models.NullBooleanField(blank=True)
    capita = models.NullBooleanField(blank=True)  # dbs was found on capita list?
    enhanced_check = models.NullBooleanField(blank=True)  # stated they have a capita dbs?
    on_update = models.NullBooleanField(blank=True)  # stated they are signed up to dbs update service?
    certificate_information = models.TextField(blank=True)  # information from dbs certificate
    within_three_months = models.NullBooleanField(blank=True)  # dbs was issued within three months of lookup?

    # Current name fields
    name_start_day = models.IntegerField(blank=True, null=True)
    name_start_month = models.IntegerField(blank=True, null=True)
    name_start_year = models.IntegerField(blank=True, null=True)
    name_end_day = models.IntegerField(blank=True, null=True)
    name_end_month = models.IntegerField(blank=True, null=True)
    name_end_year = models.IntegerField(blank=True, null=True)

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
            'adult',
            'first_name',
            'middle_names',
            'last_name',
            'birth_day',
            'birth_month',
            'birth_year',
            'relationship',
            'email',
            'dbs_certificate_number',
            'health_check_status',
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    # Date of birth property created to keep DRY
    @property
    def date_of_birth(self):
        return datetime(year=self.birth_year, month=self.birth_month, day=self.birth_day)

    @property
    def get_full_name(self):
        return '{0}{1} {2}'.format(self.first_name, " " + self.middle_names if self.middle_names else "",
                                   self.last_name)

    class Meta:
        db_table = 'ADULT_IN_HOME'

    def get_name_start_date(self):
        return date(self.name_start_year, self.name_start_month, self.name_start_day)

    def set_name_start_date(self, start_date):
        self.name_start_year = start_date.year
        self.name_start_month = start_date.month
        self.name_start_day = start_date.day

    start_date = property(get_name_start_date, set_name_start_date)

    def get_name_end_date(self):
        return date(self.name_end_year, self.name_end_month, self.name_end_day)

    def set_name_end_date(self, end_date):
        self.name_end_year = end_date.year
        self.name_end_month = end_date.month
        self.name_end_day = end_date.day

    end_date = property(get_name_end_date, set_name_end_date)
