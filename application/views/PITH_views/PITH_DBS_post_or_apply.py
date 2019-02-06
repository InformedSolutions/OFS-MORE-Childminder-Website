import logging
import enum

from datetime import datetime
from collections import defaultdict

from application.models import AdultInHome
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView
from application import dbs
from application.business_logic import date_issued_within_three_months


# Initiate logging
log = logging.getLogger('')


class DBSRequirement(enum.Enum):

    APPLY_FOR_NEW = 0
    UPDATE_SERVICE_SIGN_UP = 1
    UPDATE_SERVICE_CHECK = 2


class PITHDBSPostOrApplyView(PITHTemplateView):

    template_name = 'PITH_templates/PITH_DBS_post_or_apply.html'
    success_url = 'PITH-Children-Check-View'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for caching info which is the result of dbs lookup
        self.adults_requiring_dbs_action = None

    def get_context_data(self, **kwargs):

        application_id = get_id(self.request)

        adult_lists = defaultdict(list)

        for adult, dbs_req in self.get_adults_requiring_dbs_action(application_id):

            adult_lists['adult_dbs_list_{}'.format(dbs_req.name.lower())].append(adult)

        kwargs.update(adult_lists)

        return super().get_context_data(**kwargs)

    def get_adults_requiring_dbs_action(self, application_id):
        """
        Gets the list of adults in the home associated with this application that need to
        take further action to complete their DBS check
        :param application_id:
        :return: List of 2-tuples containing the adult model and a DBSRequirement enum
            describing the action required regarding their DBS
        """

        if self.adults_requiring_dbs_action is not None:
            return self.adults_requiring_dbs_action

        adults = AdultInHome.objects.filter(application_id=application_id)
        filtered = []
        for adult in adults:

            # fetch dbs record
            dbs_record = getattr(dbs.read(adult.dbs_certificate_number), 'record', None)

            # No dbs at all
            if dbs_record is None and not adult.capita:
                filtered.append((adult, DBSRequirement.APPLY_FOR_NEW))

            # requires updating
            elif (dbs_record is None and adult.capita) \
                    or (dbs_record is not None and not self.dbs_last_three_months(dbs_record)):

                if adult.on_update:
                    filtered.append((adult, DBSRequirement.UPDATE_SERVICE_CHECK))
                else:
                    filtered.append((adult, DBSRequirement.UPDATE_SERVICE_SIGN_UP))

        self.adults_requiring_dbs_action = filtered
        return filtered

    def dbs_last_three_months(self, dbs_record):
        issue_datetime = datetime.strptime(dbs_record['date_of_issue'], '%Y-%m-%d')
        return date_issued_within_three_months(issue_datetime)