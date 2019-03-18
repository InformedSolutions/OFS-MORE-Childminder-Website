from datetime import date
from uuid import uuid4

from django.db import models


class PreviousAddress(models.Model):
    """
    Model for PREVIOUS_ADDRESS table, used to contain previous
    """
    # Options for type discriminator
    previous_name_types = (
        ('ADULT', 'ADULT'),
        ('CHILD', 'CHILD'),
        ('APPLICANT', 'APPLICANT'),
    )

    # Primary key
    previous_name_id = models.UUIDField(primary_key=True, default=uuid4)

    # Foreign key for both adult and child in home
    person_id = models.UUIDField(blank=True)

    # Type discriminator
    person_type = models.CharField(choices=previous_name_types, max_length=50, blank=True)

    street_line1 = models.CharField(max_length=100, blank=True)
    street_line2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=100, blank=True)

    # Date fields
    moved_in_day = models.IntegerField(blank=True, null=True)
    moved_in_month = models.IntegerField(blank=True, null=True)
    moved_in_year = models.IntegerField(blank=True, null=True)
    moved_out_day = models.IntegerField(blank=True, null=True)
    moved_out_month = models.IntegerField(blank=True, null=True)
    moved_out_year = models.IntegerField(blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'PREVIOUS_ADDRESS'

    def get_moved_in_date(self):
        return date(self.moved_in_year, self.moved_in_month, self.moved_in_day)

    def set_moved_in_date(self, moved_in_date):
        self.moved_in_year = moved_in_date.year
        self.moved_in_month = moved_in_date.month
        self.moved_in_day = moved_in_date.day

    moved_in_date = property(get_moved_in_date, set_moved_in_date)

    def get_moved_out_date(self):
        return date(self.moved_out_year, self.moved_out_month, self.moved_out_day)

    def set_moved_out_date(self, moved_out_date):
        self.moved_out_year = moved_out_date.year
        self.moved_out_month = moved_out_date.month
        self.moved_out_day = moved_out_date.day

    moved_out_date = property(get_moved_out_date, set_moved_out_date)
