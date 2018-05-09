from .view_parent import *


class ExistingApplicationTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/sign-in/')
        self.assertEqual(found.func, existing_email)