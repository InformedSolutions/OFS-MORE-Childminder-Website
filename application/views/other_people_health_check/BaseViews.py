from django.core.exceptions import ImproperlyConfigured
from django.views.generic import FormView, TemplateView

from application.utils import build_url


class BaseFormView(FormView):
    """
    This is the base interface from which the rest of the other people health check views inherit from
    It contains a set of base methods to aid in page design/workflow, see the django documentation on GCBVs for details
    """

    # Used in the generation of the url for a successful form submission's destination
    success_url = None
    success_parameters = {}

    def get_context_data(self, **kwargs):
        """
        Get context data passes arguments into the template context for the view
        :param kwargs:
        :return: a dictionary containing all the data to be rendered
        """

        context = super(BaseFormView, self).get_context_data()
        # Much like the general application has an application id, this person id must be present at all times
        context['person_id'] = self.request.GET['person_id']

        return context

    def get_success_url(self):
        """
        Get success url is called whenever a successful form submission occurs, it generates a url based off of
        success_url and success_parameters as defined in the class definition
        :return: a full url for the next page
        """

        if self.success_url:
            # If not none, run the build url util function
            url = build_url(self.success_url, get=self.get_success_parameters())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def get_success_parameters(self):
        """
        Custom method to generate the list of get parameters for the success_url
        :return: a dictionary containing each of the pieces of data to be sent
        """
        params = dict()
        params['person_id'] = self.request.GET['person_id']

        return params


class BaseTemplateView(TemplateView):
    """
    Base Template view is used for any pages that do not require a form, but still require some context data
    """

    # Used in instantiation to generate the link for the template
    success_url_name = None

    def get_context_data(self, **kwargs):
        """
        Get context data passes arguments into the template context for the view, in this case, the link to be followed
        :param kwargs:
        :return:
        """
        context = super(BaseTemplateView, self).get_context_data(**kwargs)
        person_id = self.request.GET['person_id']
        context['link_url'] = build_url(self.success_url_name, get={'person_id': person_id})

        return context
