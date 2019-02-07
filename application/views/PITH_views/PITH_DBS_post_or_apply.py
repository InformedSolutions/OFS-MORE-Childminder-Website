import logging

from datetime import datetime
from collections import defaultdict

from application.models import AdultInHome
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView
from application.business_logic import find_dbs_status, DBSStatus


# Initiate logging
log = logging.getLogger('')


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

        for adult, dbs_status in self.get_adults_requiring_dbs_action(application_id):

            adult_lists['{}_list'.format(dbs_status.name.lower())].append(adult)

        kwargs.update(adult_lists)

        return super().get_context_data(**kwargs)

    def get_adults_requiring_dbs_action(self, application_id):
        """
        Gets the list of adults in the home associated with this application that need to
        take further action to complete their DBS check
        :param application_id:
        :return: List of 2-tuples containing the adult model and their DBSStatus
        """

        if self.adults_requiring_dbs_action is not None:
            return self.adults_requiring_dbs_action

        adults = AdultInHome.objects.filter(application_id=application_id)
        filtered = []
        for adult in adults:

            dbs_status = find_dbs_status(adult.dbs_certificate_number, adult, adult.capita, adult.on_update)

            if dbs_status in (DBSStatus.NEED_APPLY_FOR_NEW,
                              DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP,
                              DBSStatus.NEED_UPDATE_SERVICE_CHECK):
                filtered.append((adult, dbs_status))

        self.adults_requiring_dbs_action = filtered
        return filtered