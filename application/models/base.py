"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- models.py --

@author: Informed Solutions
"""
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms.models import model_to_dict

from application.identity_gateway import IdentityGatewayActions


TASK_STATUS = (
    ('NOT_STARTED', 'NOT_STARTED'),
    ('FLAGGED', 'FLAGGED'),
    ('COMPLETED', 'COMPLETED')
)


class RetrofitAPIModel:  # API Model Manager
    """
    Class for the existing childminder models to talk to the Childminder Gateway API instead of using the
    Django model manager - in effect, a variant on the models.Manager class.
    """

    def filter(self, **kwargs):
        """
        Run a list against db with given kwargs.
        """
        try:
            record = IdentityGatewayActions().list('user', params=kwargs).record
        except Exception as e:
            if e.error.title == '404 Not Found':
                # return models.QuerySet()  # Return blank QuerySet if nothing found.
                # return self.manager.none()
                return ChildminderQuerySet()
            else:

                raise e

    def get(self, **kwargs):
        """
        Run query against db with given kwargs.
        """
        try:
            record = IdentityGatewayActions().list('user', params=kwargs).record
        except Exception as e:
            if e.error.title == '404 Not Found':  # CM expects ObjectDoesNotExist error if 404 when calling "get".
                raise ObjectDoesNotExist
            else:
                raise e
        # return models.Q(record)
        # return IdentityGatewayActions().read('user', params)
        for key, value in record.items():
            setattr(self, key, value)
        return self

    def save(self):
        """
        Update record in database using values stored in the model.
        """
        IdentityGatewayActions().patch('user', params=self.get_api_call_params())

    def create(self, **kwargs):
        """
        Make a POST request to the Gateway using kwargs supplied.
        """
        # TODO: When CM gateway implemented for all models, below won't work.
        if isinstance(kwargs['application_id'], models.Model):  # Application object sometimes passed as argument.
            kwargs['application_id'] = str(kwargs['application_id'].application_id)
        IdentityGatewayActions().create('user', params=kwargs)

    def get_api_call_params(self):
        """
        Create a dict of params to pass to API call given some object with attributes.
        """
        return {k: v for k, v in vars(self).items() if not k.startswith('_') and not callable(k)}


class ChildminderQuerySet:
    """
    Adapter class for converting the API model manager's dictionary return values to a Django Queryset.
    """

    def __init__(self, record=None):
        self.record = record

    def exists(self):
        return self.record is None
