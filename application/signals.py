"""Signals

https://docs.djangoproject.com/en/dev/topics/signals/
"""

import sys
import traceback

from timeline_logger.models import TimelineLog
from application.models import Application

def timelog_post_init(sender, instance, **kwargs):
    """
    Signal for post_init() saves original data for the future usage in post_save()
    """

    try:
        for field in instance.timelog_fields:
            setattr(instance, '_original_%s' % field, getattr(instance, field))
    except AttributeError:
        traceback.print_exc(file=sys.stdout)
        sys.exit('''
            -------------------------------------------------------------------
            Sorry your model doesn't have timelog_fields method. You can't use
            timelog without specifying which fields to log in your model.
            -------------------------------------------------------------------
        ''')


def timelog_post_save(sender, instance, created, **kwargs):
    """
    When post_save() called for specified Models trigger this signal

    This signal is searching for fields defined in timelog_fields()
    in a model which caught this signal. After that checks changed
    value and writes changes to the timelogger.
    """

    try:
        status = Application.objects.get(pk=instance.application_id.pk).application_status
    except AttributeError:
        traceback.print_exc(file=sys.stdout)
        sys.exit('''
            ------------------------------------------------------------------
            Sorry your model doesn't have application_id field, you can't use
            timelog without this field in your model.
            ------------------------------------------------------------------
        ''')

    instance.refresh_from_db()

    if status == 'FURTHER_INFORMATION':
        for field in instance.timelog_fields:
            value = getattr(instance, field)
            orig_value = getattr(instance, '_original_%s' % field)
            if value != orig_value:
                TimelineLog.objects.create(
                    content_object=instance.application_id,
                    user=None,
                    template='timeline_logger/application_field.txt',
                    extra_data={
                        'user_type': 'applicant',
                        'application_status': status,
                        'field': field,
                        'action': 'updated'
                    }
                )
