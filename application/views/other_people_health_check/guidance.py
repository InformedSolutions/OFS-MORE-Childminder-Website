from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseTemplateView


class Guidance(BaseTemplateView):
    """
    Template view to  render the guidance page on being successfully validated by dob_auth
    """
    template_name = "other_people_health_check/guidance.html"
    success_url_name = 'Health-Check-Current'
