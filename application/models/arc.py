from uuid import uuid4
from django.db import models
from .base import TASK_STATUS

class Arc(models.Model):
    application_id = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.CharField(max_length=50, blank=True)
    last_accessed = models.CharField(max_length=50)
    app_type = models.CharField(max_length=50)
    comments = models.CharField(blank=True, max_length=400)
    # What was previously ArcStatus is below
    login_details_review = models.CharField(choices=TASK_STATUS, max_length=50)
    childcare_type_review = models.CharField(choices=TASK_STATUS, max_length=50)
    personal_details_review = models.CharField(choices=TASK_STATUS, max_length=50)
    first_aid_review = models.CharField(choices=TASK_STATUS, max_length=50)
    dbs_review = models.CharField(choices=TASK_STATUS, max_length=50)
    health_review = models.CharField(choices=TASK_STATUS, max_length=50)
    references_review = models.CharField(choices=TASK_STATUS, max_length=50)
    people_in_home_review = models.CharField(choices=TASK_STATUS, max_length=50)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'ARC'
