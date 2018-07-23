from uuid import uuid4

from django.db import models
from .adult_in_home import AdultInHome


class OtherPersonPreviousRegistrationDetails(models.Model):
    """
    Model for PREVIOUS_REGISTRATION_DETAILS table
    """
    previous_registration_id = models.UUIDField(primary_key=True, default=uuid4)
    person_id = models.ForeignKey(AdultInHome, on_delete=models.CASCADE, db_column='person_id')
    previous_registration = models.BooleanField(default=False)
    individual_id = models.IntegerField(default=0, null=True, blank=True)
    five_years_in_UK = models.BooleanField(default=False)

    @classmethod
    def get_id(cls, person_id):
        return cls.objects.get(person_id=person_id)

    class Meta:
        db_table = 'OTHER_PERSON_PREVIOUS_REGISTRATION_DETAILS'
