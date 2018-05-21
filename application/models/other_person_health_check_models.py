from uuid import uuid4

from django.db import models

from .adult_in_home import AdultInHome


class HealthCheckBase(models.Model):

    illness_id = models.UUIDField(
        primary_key=True,
        default=uuid4
    )

    person_id = models.ForeignKey(
        AdultInHome,
        on_delete=models.CASCADE,
        blank=True
    )

    description = models.CharField(max_length=150)

    class Meta:
        abstract = True


class HealthCheckHospital(HealthCheckBase):
    start_date = models.DateField()

    end_date = models.DateField()

    class Meta(HealthCheckBase.Meta):
        db_table = 'HOSPITAL_ADMISSION'
        ordering = ['start_date']


class HealthCheckSerious(HealthCheckBase):
    start_date = models.DateField()

    end_date = models.DateField()

    class Meta(HealthCheckBase.Meta):
        db_table = 'SERIOUS_ILLNESS'
        ordering = ['start_date']


class HealthCheckCurrent(HealthCheckBase):

    class Meta:
        db_table = 'CURRENT_ILLNESS'

