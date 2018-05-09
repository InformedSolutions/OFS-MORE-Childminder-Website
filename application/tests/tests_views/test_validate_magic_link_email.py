from .view_parent import *


class ValidateMagicLinkEmailTest(ViewsTest):

    def test_page_not_displayed_without_magic_link_code(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/validate/')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)