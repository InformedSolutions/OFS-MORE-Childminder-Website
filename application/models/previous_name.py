from datetime import date
from uuid import uuid4
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .application import Application
from .adult_in_home import AdultInHome
from .child_in_home import ChildInHome


class PreviousName(models.Model):
    """
    Model for PREVIOUS_NAME table, used to contain previous
    """
    # Options for type discriminator
    previous_name_types = (
        ('ADULT', 'ADULT'),
        ('CHILD', 'CHILD'),
        ('APPLICANT', 'APPLICANT')
    )

    # Primary key
    previous_name_id = models.UUIDField(primary_key=True, default=uuid4)

    # Foreign key for both adult and child in home
    person_id = models.UUIDField(blank=True)

    # Type discriminator
    other_person_type = models.CharField(choices=previous_name_types, max_length=200, blank=True)

    # Actual name fields
    first_name = models.CharField(max_length=200, blank=True)
    middle_names = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)

    # Date fields
    start_day = models.IntegerField(blank=True, null=True)
    start_month = models.IntegerField(blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True)
    end_day = models.IntegerField(blank=True, null=True)
    end_month = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)

    @property
    def person(self):
        """
        Wrapper method so that fetching the foreign key is more generic
        :return: Return the key that exists for the record, or an assertion error should neither key have been set
        """
        if self.adult_id is not None and self.child_id is not None:
            raise AssertionError("Both 'adult_id' and 'child_id' have been set, this cannot occur")
        elif self.adult_id is not None:
            return self.adult_id
        elif self.child_id is not None:
            return self.child_id
        else:
            raise AssertionError("Neither 'adult_id' or 'child_id' is set")

    class Meta:
        db_table = 'PREVIOUS_NAME'

    def get_start_date(self):
        return date(self.start_year, self.start_month, self.start_day)

    def set_start_date(self, start_date):
        self.start_year = start_date.year
        self.start_month = start_date.month

    start_date = property(get_start_date, set_start_date)

    def get_end_date(self):
        return date(self.end_year, self.end_month, self.end_day)

    def set_end_date(self, end_date):
        self.end_year = end_date.year
        self.end_month = end_date.month

    end_date = property(get_end_date, set_end_date)