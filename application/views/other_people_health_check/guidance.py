from application.models import AdultInHome
from application.views.other_people_health_check.BaseViews import BaseTemplateView


class Guidance(BaseTemplateView):
    """
    Template view to  render the guidance page on being successfully validated by dob_auth
    """
    template_name = "other_people_health_check/guidance.html"
    success_url_name = 'Health-Check-Current'

    def post(self, request=None):
        """
        extension of the inbuilt post method to add the times wrong value from the post request to the object
        :param request:
        :return:
        """
        response = super().post(request=self.request)

        return response
