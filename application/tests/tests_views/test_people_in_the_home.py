from django.test import modify_settings, tag

from application.utils import build_url
from application.views import PITH_views
from application.models import AdultInHome
from .view_parent import *

@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class PITHTestCase(ViewsTest):
    view = None
    url_name = None

    # SET UP - Function run when (sub)class instantiated.

    def setUp(self):
        self.client = Client()
        self.application_id = 'aa22b6dd-0a77-4887-839d-48d1253fe52c'

    # UTILITY FUNCTIONS

    def createApplication(self):
        self.application = Application.objects.create(application_id=self.application_id)
        return self.application

    def deleteApplication(self):
        self.application = None
        return self.application.delete()

    def createAdultInHome(self, lived_abroad=True, military_base=True, capita=True, on_update=None, dbs_certificate_number='123412341234'):

        adult_id = '421a5a45-48ae-48c0-8dac-3ae7e654bdf4'
        first_name = 'Timmy'
        last_name = 'Tester'
        birth_day = '31'
        birth_month = '03'
        birth_year = '1980'
        relationship = 'Friend'
        email = 'Test@Test.com'

        self.adult_in_home = AdultInHome.objects.create(adult_id=adult_id,
                                                        adult=1,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        birth_day=birth_day,
                                                        birth_month=birth_month,
                                                        birth_year=birth_year,
                                                        relationship=relationship,
                                                        email=email,
                                                        application_id=self.application_id,
                                                        lived_abroad=lived_abroad,
                                                        military_base=military_base,
                                                        capita=capita,
                                                        on_update=on_update,
                                                        dbs_certificate_number=dbs_certificate_number,
                                                        )

        return self.adult_in_home

    # TEST TEMPLATES

    def url_resolves_to_page(self):
        found = resolve(build_url(self.url_name))

        # Compares view found to view passed.
        self.assertEqual(found.func.view_class, self.view)

    def post_success_url(self, success_url, data, application_created=False):
        """
        This test template is intended to check that a post request to a page with a given data returns the correct
        response code and url.
        :param success_url: The name of the intended url to be redirected to.
        :param data: Any context data passed to the view.
        :param application_created: Boolean to determine whether or not to create an Application instance.
        :return:
        """
        url = build_url(self.url_name)

        if not application_created:
            self.createApplication()

        response = self.client.post(url, data)

        # Check that a redirect response was returned.
        if not response.status_code == 302:
            print('Returned response code {0}, not 302'.format(response.status_code))
        self.assertEqual(response.status_code, 302)

        # Check that the correct url was redirected to.
        if not build_url(success_url) in response.url:
            print('{0} is not in {1}'.format(build_url(success_url), response.url))
        self.assertTrue(build_url(success_url) in response.url)

        self.deleteApplication()


class PITHGuidanceTests(PITHTestCase):
    view = PITH_views.PITHGuidanceView
    url_name = 'PITH-Guidance-View'
    success_url = 'PITH-Adult-Check-View'

    @tag('PITH', 'unit')
    def test_url_resolves_to_page(self):
        super().url_resolves_to_page()

    @tag('PITH', 'http')
    def test_redirect_on_post(self):
        url = self.success_url
        data = {
            'id': self.application_id
        }
        super().post_success_url(url, data)


class PITHAdultCheckTests(PITHTestCase):
    view = PITH_views.PITHAdultCheckView
    url_name = 'PITH-Adult-Check-View'
    success_url = ('PITH-Adult-Details-View', 'PITH-Children-Check-View')

    @tag('PITH', 'unit')
    def test_url_resolves_to_page(self):
        super().url_resolves_to_page()

    @tag('PITH', 'http')
    def test_redirect_on_post_adult_in_home(self):
        url = self.success_url[0]
        data = {
            'id': self.application_id,
            'adults_in_home': True
        }
        super().post_success_url(url, data)

    @tag('PITH', 'http')
    def test_redirect_on_post_no_adult_in_home(self):
        url = self.success_url[1]
        data = {
            'id': self.application_id,
            'adults_in_home': False
        }
        super().post_success_url(url, data)

class PITHLivedAbroadTests(PITHTestCase):
    view = PITH_views.PITHAdultCheckView
    url_name = 'PITH-Lived-Abroad-View'
    success_url = ('PITH-Abroad-Criminal-View', 'PITH-DBS-Check-View', 'PITH-Military-Base-View')

    @tag('PITH', 'unit')
    def test_url_resolves_to_page(self):
        super().url_resolves_to_page()

    @tag('PITH', 'http')
    def test_redirect_on_post_adult_in_home(self):
        url = self.success_url[0]
        data = {
            'id': self.application_id,
            'lived_abroad': True
        }
        super().post_success_url(url, data)

    @tag('PITH', 'http')
    def test_redirect_on_post_no_adult_in_home(self):
        url = self.success_url[1]
        data = {
            'id': self.application_id,
            'adults_in_home': False
        }
        super().post_success_url(url, data)


class PITHDBSChecksView(PITHTestCase):
    view = PITH_views.PITHDBSCheckView
    url_name = 'PITH-DBS-Check-View'
    success_url = ('PITH-Post-View', 'PITH-Apply-View', 'PITH-Children-Check-View')

    @tag('PITH', 'http')
    def test_url_resolves_to_page(self):
        super().url_resolves_to_page()

    @tag('PITH', 'http')
    def test_redirect_on_yes_to_update_service(self):
        url = self.success_url[0]

        adult = super().createAdultInHome(capita=None, on_update=True, dbs_certificate_number='123456654321')

        data = {
            'id': self.application_id,
            ''
        }

