from django.db import models


class CapitaDBSFile(models.Model):
    """
    Model to store the last filename used to update the DBS API.
    """
    filename = models.CharField(max_length=100)
    date_uploaded = models.DateField()

    class Meta:
        db_table = 'CAPITA_DBS_FILE'
