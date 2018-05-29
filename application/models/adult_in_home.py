from datetime import datetime
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
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    validated = models.BooleanField(default=False)
    current_treatment = models.NullBooleanField(null=True)
    serious_illness = models.NullBooleanField(null=True)
    hospital_admission = models.NullBooleanField(null=True)
    health_check_status = models.CharField(max_length=50, default='To do')
    email_resent = models.IntegerField(default=0)
    email_resent_timestamp = models.DateTimeField(null=True, blank=True)

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
            'health_check_status'
        )

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    # Date of birth property created to keep DRY
    @property
    def date_of_birth(self):
        return datetime(year=self.birth_year, month=self.birth_month, day=self.birth_day)

    class Meta:
        db_table = 'ADULT_IN_HOME'
