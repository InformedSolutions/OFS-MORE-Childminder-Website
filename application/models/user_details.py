
from uuid import uuid4

from django.db import models

class UserDetails(models.Model):
    """
    Model for USER_DETAILS table
    """
    login_id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    add_phone_number = models.CharField(max_length=20, blank=True)
    email_expiry_date = models.IntegerField(blank=True, null=True)
    sms_expiry_date = models.IntegerField(blank=True, null=True)
    magic_link_email = models.CharField(max_length=100, blank=True, null=True)
    magic_link_sms = models.CharField(max_length=100, blank=True, null=True)
    security_question = models.CharField(max_length=100, blank=True, null=True)
    security_answer = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'USER_DETAILS'
