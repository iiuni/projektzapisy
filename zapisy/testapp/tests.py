"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# from django.test import TestCase


# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)

from django.test import LiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from django.contrib.auth.models import User
from apps.news.models import News

class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(SeleniumTestCase, cls).tearDownClass()
        cls.selenium.quit()


class MyAppTests(SeleniumTestCase):

    def test_form(self):
        user = User.objects.create_user('foo', password = 'bar')
        user.save()
        n = News(title = "Przykladowy news", body = "Tresc newsa", category = "offer", author = user)
        n.save()
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.get_screenshot_as_file("screenshot.png")
        # username = self.selenium.find_element_by_name('username')
        # username.send_keys('bennylope')
        # self.selenium.find_element_by_name('submit').click()

    # def test_form_validation(self):
    #     """Validate the form with JavaScript"""
    #     self.selenium.get('%s%s' % (self.live_server_url, '/'))
    #     first_name = self.selenium.find_element_by_name('first_name')
    #     first_name.send_keys('ben')
    #     last_name = self.selenium.find_element_by_name('last_name')
    #     last_name.send_keys('lopatin')
    #     self.selenium.find_elements(By.XPATH, "//input[@value='benlopatin']")
