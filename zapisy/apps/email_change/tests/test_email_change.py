import re
from unittest import TestCase

from django.core import mail
from django.test import Client
from django.contrib.auth.models import User


class EmailChangeTest(TestCase):
    def createUser(self):
        self.password = '11111'
        self.username = 'przemka'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email='admin@admin.com')
        self.user.save()

    def setUp(self):
        self.createUser()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_email_change(self):
        response = self.client.get("/accounts/email/change/")
        self.assertNotEqual(len(re.findall('id_email', str(response.content))), 0)
        current_len = len(mail.outbox)
        self.client.post("/accounts/email/change/", {"email": 'lorem@ipsum.com'},
                         follow=True)
        self.assertEqual(len(mail.outbox), current_len + 1)
