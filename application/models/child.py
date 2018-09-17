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

    def get_full_name(self):
        if len(self.middle_names) > 0:
            concatenated_name = self.first_name + " " \
                                + self.middle_names + " " + self.last_name
        else:
            concatenated_name = self.first_name + " " + self.last_name

        return concatenated_name

    class Meta:
        db_table = 'CHILD'
