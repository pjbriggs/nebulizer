#!/usr/bin/env python

import unittest
from nebulizer.users import User
from nebulizer.users import check_username_format
from nebulizer.users import get_username_from_login
from nebulizer.users import validate_password

class TestUser(unittest.TestCase):
    """
    Tests for the 'User' class

    """
    def test_load_user_data_minimal(self):
        # Data returned from galaxy.users.UserClient(gi).get_users()
        user_data = { 'username': 'bloggs',
                      'model_class': 'User',
                      'id': 'd6fbfd317568bb93',
                      'email': 'joe.bloggs@galaxy.org' }
        user = User(user_data)
        self.assertEqual(user.username,'bloggs')
        self.assertEqual(user.email,'joe.bloggs@galaxy.org')
        self.assertEqual(user.id,'d6fbfd317568bb93')
        self.assertEqual(user.display_status,'')
    def test_load_user_data_full(self):
        # Data returned from galaxy.users.UserClient(gi).show_user()
        user_data = { 'username': 'bloggs',
                      'quota_percent': 4,
                      'total_disk_usage': 13181590307.0,
                      'nice_total_disk_usage': '12.3 GB',
                      'id': 'd6fbfd317568bb93',
                      'is_admin': True,
                      'tags_used': [],
                      'model_class': 'User',
                      'email': 'joe.bloggs@galaxy.org',
                      'active': True,
                      'deleted': False,
                      'purged': False, }
        user = User(user_data)
        self.assertEqual(user.username,'bloggs')
        self.assertEqual(user.email,'joe.bloggs@galaxy.org')
        self.assertEqual(user.id,'d6fbfd317568bb93')
        self.assertEqual(user.quota_percent,4)
        self.assertEqual(user.total_disk_usage,13181590307.0)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.nice_total_disk_usage,'12.3 GB')
        self.assertEqual(user.display_status,'active')

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
