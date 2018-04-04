from uuid import uuid4
from django.db import models
from .application import Application


class UserDetails(models.Model):
    """
    Model for USER_DETAILS table
    """
    login_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id', default=uuid4)
    email = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    add_phone_number = models.CharField(max_length=20, blank=True)
    email_expiry_date = models.IntegerField(blank=True, null=True)
    sms_expiry_date = models.IntegerField(blank=True, null=True)
    magic_link_email = models.CharField(max_length=100, blank=True, null=True)
    magic_link_sms = models.CharField(max_length=100, blank=True, null=True)
    security_question = models.CharField(max_length=100, blank=True, null=True)
    security_answer = models.CharField(max_length=100, blank=True, null=True)

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
            'email',
            'mobile_number',
            'add_phone_number',
            'security_question',
            'security_answer'
        )

    class Meta:
        db_table = 'USER_DETAILS'
