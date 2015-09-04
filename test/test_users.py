#!/usr/bin/env python

import unittest
from nebulizer.users import check_username_format
from nebulizer.users import get_username_from_login
from nebulizer.users import validate_password

class TestCheckUsernameFormat(unittest.TestCase):
    def test_valid_username(self):
        self.assertTrue(check_username_format('peter-briggs'))
    def test_invalid_characters(self):
        self.assertFalse(check_username_format('J@ne!Doe'))
    def test_blank_username(self):
        self.assertFalse(check_username_format(''))

class TestGetUsernameFromLogin(unittest.TestCase):
    def test_get_username_from_login(self):
        self.assertEqual(get_username_from_login('joe.bloggs@galaxy.org'),
                         'joe-bloggs')

class TestValidatePassword(unittest.TestCase):
    def test_empty_password(self):
        self.assertFalse(validate_password(''))
    def test_invalid_password(self):
        self.assertFalse(validate_password('abc'))
    def test_valid_password(self):
        self.assertTrue(validate_password('p@55w0rd'))
