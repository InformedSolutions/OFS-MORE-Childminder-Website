from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, TemplateView
from application.utils import build_url, get_id
from application.business_logic import update_application, get_application


class PITHMultiFormView(TemplateView, TemplateResponseMixin):

    template_name = None
    form_class = None
    success_url = None
    field_name = None

    def get_context_data(self, **kwargs):
        if 'form_list' not in kwargs:
            kwargs['form_list'] = self.get_form_list()

        for form in kwargs['form_list']:
            form.check_flag()

        if sum([len(form.errors) for form in kwargs['form_list']]) != 0:
            kwargs['error_summary_list'] = [form.error_summary for form in kwargs['form_list']]
            kwargs['error_summary_title'] = self.form_class.error_summary_title

        return super().get_context_data(**kwargs)

    def get_form_kwargs(self, kwargs):
        """
        Returns the keyword arguments for instantiating the form.
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

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a list of form instances with the passed
        POST variables and then checked for validity.
        """
        form_list = self.get_form_list()

        for form in form_list:
            form.remove_flag()

        if all(form.is_valid() for form in form_list):
            return self.form_valid(form_list)
        else:
            return self.form_invalid(form_list)

    def form_valid(self, form_list):
        """
        If the form is valid, redirect to the supplied URL.
        """
        application_id = get_id(self.request)

        # Update task status if flagged or completed (people_in_home_status)
        people_in_home_status = get_application(application_id, 'people_in_home_status')

        if people_in_home_status not in ['COMPLETED', 'WAITING']:
            update_application(application_id, 'people_in_home_status', 'IN_PROGRESS')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form_list):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form_list=form_list))

    def get_success_url(self, base_url=None):
        base_url = base_url or self.success_url
        application_id = get_id(self.request)
        return build_url(base_url, get={'id': application_id})

    def get_form_list(self):
        raise ImproperlyConfigured(
            "No form_list to get, please implement get_form_list")

    def get_initial(self):
        raise ImproperlyConfigured(
            "No initial data to get, please implement get_initial")
