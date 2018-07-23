from .view_parent import *


class AccountSelectionTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/sign-in/new-application/')
        self.assertEqual(found.func, account_selection)