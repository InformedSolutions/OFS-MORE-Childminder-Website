"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- models.py --

@author: Informed Solutions
"""

from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class AuditLog(models.Model):
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    audit_message = JSONField(blank=True)
    class Meta:
        managed = False
        db_table = 'AUDIT_LOG'

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
        ('COMPLETE', 'COMPLETE'),
        ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')
    )
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    login_id = models.ForeignKey(UserDetails, on_delete=models.CASCADE, db_column='login_id', blank=True, null=True)
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
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    date_accepted = models.DateTimeField(blank=True, null=True)
    order_code = models.UUIDField(blank=True, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'APPLICATION'


class ChildcareType(models.Model):
    """
    Model for CHILDCARE_TYPE table
    """
    childcare_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    zero_to_five = models.BooleanField()
    five_to_eight = models.BooleanField()
    eight_plus = models.BooleanField()

    class Meta:
        db_table = 'CHILDCARE_TYPE'


class ApplicantPersonalDetails(models.Model):
    """
    Model for APPLICANT_PERSONAL_DETAILS table
    """
    personal_detail_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    birth_day = models.IntegerField(blank=True, null=True)
    birth_month = models.IntegerField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'APPLICANT_PERSONAL_DETAILS'


class ApplicantName(models.Model):
    """
    Model for APPLICANT_NAME table
    """
    name_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
    current_name = models.BooleanField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'APPLICANT_NAME'


class ApplicantHomeAddress(models.Model):
    """
    Model for APPLICANT_HOME_ADDRESS table
    """
    home_address_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
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

    class Meta:
        db_table = 'APPLICANT_HOME_ADDRESS'


class FirstAidTraining(models.Model):
    """
    Model for FIRST_AID_TRAINING table
    """
    first_aid_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    training_organisation = models.CharField(max_length=100)
    course_title = models.CharField(max_length=100)
    course_day = models.IntegerField()
    course_month = models.IntegerField()
    course_year = models.IntegerField()
    show_certificate = models.NullBooleanField(blank=True, null=True, default=None)
    renew_certificate = models.NullBooleanField(blank=True, null=True, default=None)

    class Meta:
        db_table = 'FIRST_AID_TRAINING'


class EYFS(models.Model):
    """
    Model for EYFS table
    """
    eyfs_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    eyfs_understand = models.NullBooleanField(blank=True, null=True, default=None)
    eyfs_training_declare = models.NullBooleanField(blank=True, null=True, default=None)
    eyfs_questions_declare = models.NullBooleanField(blank=True, null=True, default=None)

    class Meta:
        db_table = 'EYFS'


class CriminalRecordCheck(models.Model):
    """
    Model for CRIMINAL_RECORD_CHECK table
    """
    criminal_record_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    cautions_convictions = models.BooleanField(blank=True)
    send_certificate_declare = models.NullBooleanField(blank=True)

    class Meta:
        db_table = 'CRIMINAL_RECORD_CHECK'


class HealthDeclarationBooklet(models.Model):
    """
    Model for HEALTH_DECLARATION_BOOKLET table
    """
    hdb_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    send_hdb_declare = models.NullBooleanField(blank=True)

    class Meta:
        db_table = 'HDB'


class Reference(models.Model):
    """
    Model for REFERENCE table
    """
    reference_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    reference = models.IntegerField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    years_known = models.IntegerField(blank=True)
    months_known = models.IntegerField(blank=True)
    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'REFERENCE'


class AdultInHome(models.Model):
    """
    Model for ADULT_IN_HOME table
    """
    adult_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    adult = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    dbs_certificate_number = models.CharField(max_length=50, blank=True)
    permission_declare = models.NullBooleanField(blank=True)

    class Meta:
        db_table = 'ADULT_IN_HOME'


class ChildInHome(models.Model):
    """
    Model for CHILD_IN_HOME table
    """
    child_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    child = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_day = models.IntegerField(blank=True)
    birth_month = models.IntegerField(blank=True)
    birth_year = models.IntegerField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'CHILD_IN_HOME'
