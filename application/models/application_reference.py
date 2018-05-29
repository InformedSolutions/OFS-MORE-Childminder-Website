"""
Entity definition for a table record persisting the latest available application reference number
"""

from django.core.validators import MaxValueValidator
from django.db import models


class ApplicationReference(models.Model):

    # Latest rolling reference number
    reference = models.IntegerField(validators=[MaxValueValidator(9999999)])

    class Meta:
        db_table = 'APPLICATION_REFERENCE'
