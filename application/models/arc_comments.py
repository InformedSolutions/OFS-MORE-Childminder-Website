from uuid import uuid4
from django.db import models

class ArcComments(models.Model):
    """
    Model for ARC_COMMENTS table.
    """
    review_id = models.UUIDField(primary_key=True, default=uuid4, unique=True),
    table_pk = models.UUIDField(blank=True)
    table_name = models.CharField(max_length=30, blank=True)
    field_name = models.CharField(max_length=60, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    flagged = models.BooleanField()

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'ARC_COMMENTS'
