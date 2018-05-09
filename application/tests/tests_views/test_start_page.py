from .view_parent import *


class StartPageTest(ViewsTest):

    def test_root_url_resolves_to_start_page_view(self):
        found = resolve(settings.URL_PREFIX + '/')
        self.assertEqual(found.func, start_page)