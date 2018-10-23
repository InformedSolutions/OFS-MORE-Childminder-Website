import logging

from django.core.exceptions import ObjectDoesNotExist

from application.forms.other_person_health_check.local_authorites import LocalAuthorities
from application.models import AdultInHome, HealthCheckCurrent
from application.views.other_people_health_check.BaseViews import BaseFormView

logger = logging.getLogger(__name__)


class LocalAuthorities(BaseFormView):
    """
    View to verify whether local authorities know of the household member (with respect to their own children)
    """
    template_name = 'other_people_health_check/local_authorities.html'
    form_class = LocalAuthorities
    success_url = 'Health-Check-Local-Authorities'

    def get_initial(self):
        """
        Get initial defines the initial data for the form instance that is to be rendered on the page
        :return: a dictionary mapping form field names, to values of the correct type
        """
        initial = super().get_initial()

        try:
            person_id = self.request.GET['person_id']
            person_record = AdultInHome.objects.get(pk=person_id)
            current_illness_record = HealthCheckCurrent.objects.get(person_id=person_id)
            initial['known_to_council'] = person_record.current_treatment
            initial['children_details'] = current_illness_record.description
        # If there has yet to be an entry for the model associated with the form, then no population necessary
        except ObjectDoesNotExist:
            pass

        return initial

    def form_valid(self, form):
        """
        Form valid is the function called upon a successful clean of the form instance upon a post request
        :param form: The form instance that has been validated
        :return: an http redirect to the success url
        """

        clean = form.cleaned_data
        person_id = self.request.GET['person_id']
        new_fields = {
            'person_id' :AdultInHome.objects.get(pk=person_id),
            'description': clean['illness_details']
        }

        person_record = AdultInHome.objects.get(pk=person_id)

        # If they've said no to being currently treated, if any records exist with their id, delete them
        logger.debug('Clearing current illness details for person id: ' + str(person_id) + 'as response has been renewed')
        HealthCheckCurrent.objects.filter(person_id=person_record).delete()

        if clean['currently_ill'] == 'True':
            person_record.current_treatment = True
        else:
            person_record.current_treatment = False

        if person_record.current_treatment:
            # If they say they are currently being treated, create a record saying so, or update an existing record
            # with the new data they've entered

            logger.debug('Updating current illness details for person id: ' + str(person_id))

            # Created is a boolean for verification purposes, not used here but required to call the method
            new_current_illness, created = HealthCheckCurrent.objects.update_or_create(
                person_id=person_record,
                description=clean['illness_details'],
                defaults=new_fields,
            )

        # As the current treatment boolean in the adult in home table has been updated, save the record
        person_record.save()

        return super().form_valid(form)
