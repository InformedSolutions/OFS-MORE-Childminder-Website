from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import FormView

from application.forms.other_person_health_check.current_illness import CurrentIllness
from application.models import AdultInHome, HealthCheckCurrent
from application.views.other_people_health_check.BaseViews import BaseFormView


class CurrentTreatment(BaseFormView):
    """
    View to collect information on any current illnesses the user has
    """
    template_name = 'other_people_health_check/current_treatment.html'
    form_class = CurrentIllness
    success_url = 'Health-Check-Serious-Start'

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
            initial['currently_ill'] = person_record.current_treatment
            initial['illness_details'] = current_illness_record.description
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
        if clean['currently_ill'] == 'True':
            person_record.current_treatment = True
        else:
            person_record.current_treatment = False

        if person_record.current_treatment:
            # If they say they are currently being treated, create a record saying so, or update an existing record
            # with the new data they've entered
            new_current_illness, created = HealthCheckCurrent.objects.update_or_create(
                person_id=person_record,
                description=clean['illness_details'],
                defaults=new_fields,
            )
            # Created is a boolean for verification purposes, not used here but required to call the method
        else:
            # If they've said no to being currently treated, if any records exist with their id, delete them
            deleted_illness = HealthCheckCurrent.objects.filter(person_id=person_record).delete()

        # As the current treatment boolean in the adult in home table has been updated, save the record
        person_record.save()

        return super().form_valid(form)
