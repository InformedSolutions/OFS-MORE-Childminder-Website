import logging

from application.business_logic import get_application, update_application
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView

# Initiate logging
log = logging.getLogger('')


class PITHGuidanceView(PITHTemplateView):

    template_name = 'PITH_templates/PITH_guidance.html'
    success_url = 'PITH-Adult-Check-View'

    def post(self, request, *args, **kwargs):

        application_id = get_id(request)

        # Update task status if flagged or completed (people_in_home_status)
        people_in_home_status = get_application(application_id, 'people_in_home_status')

        if people_in_home_status == 'NOT_STARTED':
            # Update the task status to 'IN_PROGRESS' from 'FLAGGED'
            update_application(application_id, 'people_in_home_status', 'IN_PROGRESS')
            log.debug('People in the home task status set to IN_PROGRESS for application ' + application_id)

        return super().post(request, *args, **kwargs)
