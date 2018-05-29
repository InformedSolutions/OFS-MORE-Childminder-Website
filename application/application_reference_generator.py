"""
Utility functions for generating a new unique application reference number
"""

from django.conf import settings
from .models import ApplicationReference, Application
import logging

logger = logging.getLogger(__name__)


def create_application_reference():
    """
    Function for getting the next available reference number that can be allocated to a Childminder application
    :return: a unique reference number for an application
    """
    try:
        last_allocated_reference_details_for_application_type = ApplicationReference.objects.all().first()

        # Roll integer field by 1
        candidate_reference = last_allocated_reference_details_for_application_type.reference + 1

        # Assert reference number has not previously been assigned
        reference_previously_allocated = Application.objects.filter(application_reference=candidate_reference).exists()

        if not reference_previously_allocated:
            # If not previously allocated, persist new latest assigned value and yield to caller
            last_allocated_reference_details_for_application_type.reference = candidate_reference
            last_allocated_reference_details_for_application_type.save()
            return settings.APPLICATION_PREFIX + str(candidate_reference)

        # In event application reference has already been allocated, recurse to attempt yield of next incremented value
        return create_application_reference()
    except Exception as e:
        logger.error('Failed to allocate application reference number: ' + str(e))

