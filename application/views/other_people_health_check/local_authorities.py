import logging

from django.core.exceptions import ObjectDoesNotExist

from application.forms.other_person_health_check.local_authorities import LocalAuthorities
from application.models import AdultInHome, HealthCheckCurrent
from application.views.other_people_health_check.BaseViews import BaseFormView

logger = logging.getLogger(__name__)


class LocalAuthorities(BaseFormView):
    """
    View to verify whether local authorities know of the household member (with respect to their own children)
    """
    template_name = 'other_people_health_check/local_authorities.html'
    form_class = LocalAuthorities
    success_url = 'Health-Check-Declaration'

    def get_initial(self):
        """
        Get initial defines the initial data for the form instance that is to be rendered on the page
        :return: a dictionary mapping form field names, to values of the correct type
        """
        initial = super().get_initial()
        person_id = self.request.GET['person_id']
        person_record = AdultInHome.objects.get(pk=person_id)
        initial['known_to_council'] = person_record.known_to_council
        initial['reasons_known_to_council_health_check'] = person_record.reasons_known_to_council_health_check

        return initial

    def form_valid(self, form):
        """
        Form valid is the function called upon a successful clean of the form instance upon a post request
        :param form: The form instance that has been validated
        :return: an http redirect to the success url
        """

        cleaned_data = form.cleaned_data
        person_id = self.request.GET['person_id']
        person_record = AdultInHome.objects.get(pk=person_id)
        if cleaned_data['known_to_council'] == 'True':
            person_record.known_to_council = True
            person_record.reasons_known_to_council_health_check = cleaned_data['reasons_known_to_council_health_check']
        else:
            person_record.known_to_council = False
            person_record.reasons_known_to_council_health_check = ''

        if person_record.known_to_council:
            logger.debug('Updating current childrens details for person id: ' + str(person_id))

        person_record.save()

        return super().form_valid(form)
