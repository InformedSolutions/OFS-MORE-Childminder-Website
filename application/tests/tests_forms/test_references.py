from django.test import TestCase
from django.urls import reverse

from application.forms import references


class TestReferences(TestCase):

    def test_time_known(self):
        test_data = {}

        for i in range(len(test_data)):
            response = self.client.post(reverse('References-First-Reference-View'),
                                        )
            self.assertFormError(response,
                                 'References-First-Reference-View',
                                 'something',
                                 'This field is required.')
