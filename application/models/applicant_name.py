from uuid import uuid4
from django.db import models
from .applicant_personal_details import ApplicantPersonalDetails
from .application import Application

class ApplicantName(models.Model):
    """
    Model for APPLICANT_NAME table
    """
    name_id = models.UUIDField(primary_key=True, default=uuid4)
    personal_detail_id = models.ForeignKey(ApplicantPersonalDetails, on_delete=models.CASCADE,
                                           db_column='personal_detail_id')
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE,
                                       db_column='application_id')
    current_name = models.BooleanField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    @classmethod
    def get_id(cls, app_id):
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id)
        return cls.objects.get(personal_detail_id=personal_detail_id)

    class Meta:
        db_table = 'APPLICANT_NAME'
