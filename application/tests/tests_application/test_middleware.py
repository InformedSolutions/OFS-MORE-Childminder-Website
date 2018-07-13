import time

from django.test import override_settings, TestCase
from django.urls import resolve, reverse

from .base import ApplicationTestBase
from application.views import SessionExpiredView


class TestMiddleware(ApplicationTestBase, TestCase):

    def setUp(self):
        super(TestMiddleware, self).TestAppInit()
        super(TestMiddleware, self).TestAppEmail()
        super(TestMiddleware, self).TestValidateEmail()
        super(TestMiddleware, self).TestAppPhone()

    @override_settings(SESSION_EXPIRY=2)
    def test_session_timeout(self):
        """
        Test to assert that the user is redirected to the 'Session-Expiry' page if their cookie is older than the
        cookie's expiry time.
        """
        response = self.client.get(reverse('Contact-Summary-View'), {'id': self.app_id})
        self.assertEqual(response.status_code, 200)

        time.sleep(3)

        response = self.client.get(reverse('Task-List-View') + '/?id=' + str(self.app_id))
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.__name__, SessionExpiredView.__name__)
