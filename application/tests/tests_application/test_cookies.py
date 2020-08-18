"""
Functional tests for cookies page

NOTE! If it throws you status 200, that means form submission is failing!

"""

from django.core.urlresolvers import reverse
from django.test import TestCase

class CookieTests(TestCase):

    def test_can_render_cookie_page(self):
        """
        Test to assert that cookies are successfully updated
        """
        response = self.client.get(reverse('Cookie-Policy'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.view_name, 'Cookie-Policy')

    def test_can_update_cookie_preference(self):
        """
        Test to confirm cookie policy can be updated
        """

        form_data = {
            'cookie_selection': 'opted_in',
            'url' : ''
        }
        response = self.client.post(reverse('Cookie-Policy'), form_data)
        self.assertEqual(response.cookies['cookie_preferences'].value, 'opted_in')