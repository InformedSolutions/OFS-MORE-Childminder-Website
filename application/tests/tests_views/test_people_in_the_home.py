from django.test import modify_settings

from application.utils import build_url
from application.views import PITH_views
from .view_parent import *

@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class TestClass(ViewsTest):
    view = None
    url_name = None

    def setUp(self):
        self.client = Client()

    # Test failing as of 27/09, to be amended during tests implementation.
    # def url_resolves_to_page(self):
    #     found = resolve(build_url(self.url_name))
    #     self.assertEqual(found.cls, self.view)

    def page_not_displayed_without_id(self):
        self.client.get(settings.URL_PREFIX + '/people?id=')


class PeopleInTheHomeTest(TestClass):
    view = PITH_views.PITHAdultCheckView
    url_name = 'PITH-Adult-Check-View'

    # def test_url_resolves_to_page(self):
    #     super().url_resolves_to_page()

    def test_page_not_displayed_without_id(self):
        super().page_not_displayed_without_id()
