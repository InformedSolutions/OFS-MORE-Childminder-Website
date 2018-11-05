from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from application.forms.other_person_health_check import dob_auth
from application.views.other_people_health_check.BaseViews import BaseFormView
from ...models import Application, AdultInHome


class DobAuthView(BaseFormView):
    """
    View to validate the entered date of birth against the stored value for the current adult in home
    """
    template_name = 'other_people_health_check/dob_auth.html'
    form_class = dob_auth.DateOfBirthAuthentication
    times_wrong = 0

    def post(self, request=None):
        """
        extension of the inbuilt post method to add the times wrong value from the post request to the object
        :param request:
        :return:
        """
        adult_id = self.request.GET.get('person_id')
        adult_record = AdultInHome.objects.get(pk=adult_id)
        application_id = adult_record.application_id_id
        application = Application.objects.get(application_id=application_id)

        # Both success_url_name and success_url required due to conflicting methods
        if application.people_in_home_arc_flagged or adult_record.health_check_status == 'COMPLETED':
            self.success_url_name = 'Health-Check-Summary'
            self.success_url = 'Health-Check-Summary'
        else:
            self.success_url_name = 'Health-Check-Guidance'

            self.success_url = 'Health-Check-Guidance'

        self.times_wrong = int(self.request.POST.get('times_wrong'))
        response = super().post(request=self.request)

        return response

    def get_context_data(self, **kwargs):
        """
        Adds the times_wrong variable to the context, having been defined in the post extension
        :param kwargs:
        :return:
        """
        context = super().get_context_data()
        context['times_wrong'] = self.times_wrong

        return context

    def get_form_kwargs(self):
        """
        Get form kwargs gives the form both the times wrong variable, and the date of birth to validate against
        :return:
        """
        kwargs = super(BaseFormView, self).get_form_kwargs()
        try:
            person_record = AdultInHome.objects.get(pk=self.request.GET['person_id'])
            kwargs['date_of_birth'] = person_record.date_of_birth.date()
            kwargs['times_wrong'] = self.times_wrong
        except ObjectDoesNotExist:
            pass

        return kwargs

    def form_invalid(self, form):
        """
        Should the form be invalid, return the super and increment times wrong
        :param form:
        :return:
        """
        self.times_wrong = self.times_wrong + 1
        response = super().form_invalid(form)

        return response
