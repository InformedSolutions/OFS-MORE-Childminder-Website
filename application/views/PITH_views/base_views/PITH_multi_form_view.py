from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from application.business_logic import update_application, get_application
from application.forms import ChildminderForms
from application.utils import build_url, get_id


class PITHMultiFormView(FormView):
    """
    Class allowing for multiple form instances on the same page.
    Intended usage is for multiple instances of the same form_class to be used, but this is dependant on
     your implementation of get_form_list.
    """
    template_name = None
    form_class = None
    success_url = None
    field_name = None

    def get_context_data(self, **kwargs) -> dict:
        """
        Method to get context data for the view.
        :param kwargs: Base context dictionary.
        :return:
        """
        if 'form_list' not in kwargs:
            kwargs['form_list'] = self.get_form_list()

        for form in kwargs['form_list']:
            form.check_flag()

        if sum([len(form.errors) for form in kwargs['form_list']]) != 0:
            kwargs['error_summary_list'] = [form.error_summary for form in kwargs['form_list']]
            kwargs['error_summary_title'] = self.form_class.error_summary_title

        return super().get_context_data(**kwargs)

    def get_form_kwargs(self, kwargs: dict) -> dict:
        """
        Returns the keyword arguments for instantiating the form.
        :param kwargs: Base form_kwargs dictionary.
        :return: Dictionary containing kwargs to be passed into form instantiation.
        """
        kwargs.update({
            'initial': self.get_initial()
        })

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return kwargs

    def get_success_url(self, get: dict = None) -> str:
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)

        if not get:
            return build_url(self.get_choice_url(application_id), get={'id': application_id})
        else:
            return build_url(self.get_choice_url(application_id), get=get)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_list = self.get_form_list()

        for form in form_list:
            form.remove_flag()

        if all(form.is_valid() for form in form_list):
            return self.form_valid(form_list)
        else:
            return self.form_invalid(form_list)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        application_id = get_id(self.request)

        # Update task status if flagged or completed (people_in_home_status)
        people_in_home_status = get_application(application_id, 'people_in_home_status')

        if people_in_home_status in ['FLAGGED', 'COMPLETED']:
            # Update the task status to 'IN_PROGRESS' from 'FLAGGED'
            update_application(application_id, 'people_in_home_status', 'IN_PROGRESS')

        return HttpResponseRedirect(self.get_success_url())

    def get_form_list(self) -> list:
        """
        A method intended to return a list of forms to instantiate.
        Specifically, intended to return a list containing instances of the same form_class.
        :return: List of ChildminderForms subclass instances.
        """
        raise ImproperlyConfigured(
            "No form_list to get, please implement get_form_list")

    def get_initial(self) -> dict:
        """
        A method intended to return initial form data.
        :return: Dict in format form_field_name: initial_value.
        """
        raise ImproperlyConfigured(
            "No initial data to get, please implement get_initial")

    def get_choice_url(self, app_id) -> str:
        """
        A method intended to return the name of a url (e.g 'PITH-Guidance-View'), for use in get_success_url.
        :param app_id: Applicant's id
        :return: String
        """
        raise ImproperlyConfigured(
            "No URL to redirect to, please implement get_choice_url")
