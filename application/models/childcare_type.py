from uuid import uuid4
from django.db import models
from .application import Application

class ChildcareType(models.Model):
    """
    Model for CHILDCARE_TYPE table
    """
    childcare_id = models.UUIDField(primary_key=True, default=uuid4)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    zero_to_five = models.BooleanField()
    five_to_eight = models.BooleanField()
    eight_plus = models.BooleanField()

    @classmethod
    def get_id(cls, app_id):
        return cls.objects.get(application_id=app_id)

    class Meta:
        db_table = 'CHILDCARE_TYPE'
