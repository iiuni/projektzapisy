from django.test import TestCase
from .factories import UserFactory
from django.core.urlresolvers import reverse


class BaseUserTestCase(TestCase):
    def test_password_check(self):
        u = UserFactory()
        self.assertTrue(u.check_password('test'))

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
