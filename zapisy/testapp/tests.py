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
