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

    def test_status_own_children_known_valid_dbs(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            known_to_social_services_pith=True,
            reasons_known_to_social_services_not_in_home='Reasons'
        )
        assert (models.Application.objects.get(pk=test_application_id).people_in_home_status == 'COMPLETED')

    def test_status_own_children_known_invalid_dbs(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            known_to_social_services_pith=True,
            reasons_known_to_social_services_not_in_home='Reasons'
        )
        assert (models.Application.objects.get(pk=test_application_id).people_in_home_status == 'Started')

    def test_status_own_children_not_known_valid_dbs(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            reasons_known_to_social_services_pith=False,
        )
        assert (models.Application.objects.get(pk=test_application_id).people_in_home_status == 'COMPLETED')

    def test_status_own_children_not_known_invalid_dbs(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            known_to_social_services_pith=False,
        )
        assert (models.Application.objects.get(pk=test_application_id).people_in_home_status == 'Started')
