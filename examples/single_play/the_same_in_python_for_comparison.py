# coding: utf-8
"""Test module description"""
import unittest
import myproductlib

from selenium import webdriver
from some_module.decorators import skip_if, bug_is_open


driver = driver = webdriver.Chrome()

urls = {'login_page': 'http://localhost:8000/login'}


class UserLoginTestCase(unittest.TestCase):
    """This class tests user login."""

    def setUp(self):
        """Arrange step."""
        self.created_user = myproductlib.user.create(
            username='foo', password='bar'
        )

    def tearDown(self):
        """Arrange step teardown"""
        self.created_user.delete()

    @skip_if(bug_is_open("bugzilla", 456789))
    def test_positive_login_with_user(self):
        """This case reproduces the user login workflow.

        :id: 12345
        :level: Critical
        :customerscenario: true
        """
        # Act
        driver.get(urls['login_page'])

        username = driver.find_element_by_name("username")
        username.clear()
        username.send_keys(self.created_user.username)

        password = driver.find_element_by_name("password")
        password.clear()
        password.send_keys(self.created_user.password)

        driver.find_element_by_css("#login_form.input[type=submit]").click()

        # Assert
        self.assertIn("Logged in as user:", driver.get_attribute('inner_html'))
