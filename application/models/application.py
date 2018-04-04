from uuid import uuid4
from django.db import models

class Application(models.Model):
    """
    Model for APPLICATION table
    """
    APP_STATUS = (
        ('ARC_REVIEW', 'ARC_REVIEW'),
        ('CANCELLED', 'CANCELLED'),
        ('CYGNUM_REVIEW', 'CYGNUM_REVIEW'),
        ('DRAFTING', 'DRAFTING'),
        ('FURTHER_INFORMATION', 'FURTHER_INFORMATION'),
        ('NOT_REGISTERED', 'NOT_REGISTERED'),
        ('REGISTERED', 'REGISTERED'),
        ('REJECTED', 'REJECTED'),
        ('SUBMITTED', 'SUBMITTED'),
        ('WITHDRAWN', 'WITHDRAWN')
    )
    APP_TYPE = (
        ('CHILDMINDER', 'CHILDMINDER'),
        ('NANNY', 'NANNY'),
        ('NURSERY', 'NURSERY'),
        ('SOCIAL_CARE', 'SOCIAL_CARE')
    )
    TASK_STATUS = (
        ('NOT_STARTED', 'NOT_STARTED'),
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
        ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')
    )
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    #login_id = models.ForeignKey(
    #    UserDetails, on_delete=models.CASCADE, db_column='login_id', blank=True, null=True)
    application_type = models.CharField(choices=APP_TYPE, max_length=50, blank=True)
    application_status = models.CharField(choices=APP_STATUS, max_length=50, blank=True)
    cygnum_urn = models.CharField(max_length=50, blank=True)
    login_details_status = models.CharField(choices=TASK_STATUS, max_length=50)
    personal_details_status = models.CharField(choices=TASK_STATUS, max_length=50)
    childcare_type_status = models.CharField(choices=TASK_STATUS, max_length=50)
    first_aid_training_status = models.CharField(choices=TASK_STATUS, max_length=50)
    eyfs_training_status = models.CharField(choices=TASK_STATUS, max_length=50)
    criminal_record_check_status = models.CharField(choices=TASK_STATUS, max_length=50)
    health_status = models.CharField(choices=TASK_STATUS, max_length=50)
    references_status = models.CharField(choices=TASK_STATUS, max_length=50)
    people_in_home_status = models.CharField(choices=TASK_STATUS, max_length=50)
    adults_in_home = models.NullBooleanField(blank=True, null=True, default=None)
    children_in_home = models.NullBooleanField(blank=True, null=True, default=None)
    children_turning_16 = models.NullBooleanField(blank=True, null=True, default=None)
    declarations_status = models.CharField(choices=TASK_STATUS, max_length=50)
    background_check_declare = models.NullBooleanField(blank=True, null=True, default=None)
    inspect_home_declare = models.NullBooleanField(blank=True, null=True, default=None)
    interview_declare = models.NullBooleanField(blank=True, null=True, default=None)
    share_info_declare = models.NullBooleanField(blank=True, null=True, default=None)
    information_correct_declare = models.NullBooleanField(blank=True, null=True, default=None)
    change_declare = models.NullBooleanField(blank=True, null=True, default=None)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    date_accepted = models.DateTimeField(blank=True, null=True)
    order_code = models.UUIDField(blank=True, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(pk=app_id)

    class Meta:
        db_table = 'APPLICATION'
