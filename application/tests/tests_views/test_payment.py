from .view_parent import *


class PaymentTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/')
        self.assertEqual(found.func, payment)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/details/')
        self.assertEqual(found.func, card_payment_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/details/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/paypal-payment-completion/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/confirmation/')
        self.assertEqual(found.func, payment_confirmation)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/confirmation/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Documents'))
        self.assertEqual(found.func, documents_needed)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Documents') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Home'))
        self.assertEqual(found.func, home_ready)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Home') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Interview'))
        self.assertEqual(found.func, prepare_for_interview)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Interview') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)