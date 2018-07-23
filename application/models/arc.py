from uuid import uuid4
from django.db import models
from .base import TASK_STATUS


class Arc(models.Model):
    """
    Model for the ARC table.
    """
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=50, blank=True)
    last_accessed = models.CharField(max_length=50)
    app_type = models.CharField(max_length=50)
    # What was previously ArcStatus is below
    login_details_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    childcare_type_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    personal_details_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    first_aid_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    eyfs_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    dbs_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    health_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    references_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')
    people_in_home_review = models.CharField(choices=TASK_STATUS, max_length=50, default='NOT_STARTED')

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'ARC'
