import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from utils.browser import make_chrome_browser


class RecipeHomePageFunctionalTest(StaticLiveServerTestCase):
    def sleep(self, seconds=1):
        time.sleep(seconds)

    def test_the_test(self):
        browser = make_chrome_browser()
        browser.get(self.live_server_url)
        self.sleep(1)
        body = browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Sem receitas',body.text)
        browser.quit()