from django.db import models

from .childbase import ChildBase


class Child(ChildBase):
    """
    Model for CHILD_OUTSIDE_HOME table
    """
    lives_with_childminder = models.NullBooleanField(blank=True)

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CHILD'
