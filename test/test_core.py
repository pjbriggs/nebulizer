#!/usr/bin/env python

import unittest
import tempfile
import shutil
import os
from nebulizer.core import Credentials

class TestCredentials(unittest.TestCase):
    """
    Tests for the 'Credentials' class

    """
    def setUp(self):
        # Create temp working dir
        self.tmpdir = tempfile.mkdtemp(suffix='TestCredentials')

    def tearDown(self):
        # Remove the temporary test directory
        shutil.rmtree(self.tmpdir)

    def _make_key_file(self):
        # Create a key file for testing
        tmp_key_file = os.path.join(self.tmpdir,'.nebulizer')
        with open(tmp_key_file,'w') as fp:
            fp.write("""# .nebulizer
production\thttp://prod.example.org\t37b6444b8c62a137ab306242
devel\thttp://devel.example.org\t137ab30624237b6444b8c62a
local\thttp://127.0.0.1:8080\tb8c62624237b6444137ab30
""")
        return tmp_key_file

    def test_list_keys(self):
        """
        Credentials.list_keys: lists aliases
        """
        tmp_key_file = self._make_key_file()
        credentials = Credentials(key_file=tmp_key_file)
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'devel',
                          'local'])

    def test_fetch_key(self):
        """
        Credentials.fetch_key: fetches correct data from key file
        """
        tmp_key_file = self._make_key_file()
        credentials = Credentials(key_file=tmp_key_file)
        self.assertEqual(credentials.fetch_key('production'),
                         ('http://prod.example.org',
                          '37b6444b8c62a137ab306242'))
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel.example.org',
                          '137ab30624237b6444b8c62a'))
        self.assertEqual(credentials.fetch_key('local'),
                         ('http://127.0.0.1:8080',
                          'b8c62624237b6444137ab30'))
        self.assertEqual(credentials.fetch_key('http://devel.example.org'),
                         ('http://devel.example.org',
                          '137ab30624237b6444b8c62a'))
        self.assertRaises(KeyError,credentials.fetch_key,'nonexistent')

    def test_store_key(self):
        """
        Credentials.store_key: appends new key to key file
        """
        tmp_key_file = self._make_key_file()
        credentials = Credentials(key_file=tmp_key_file)
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'devel',
                          'local'])
        credentials.store_key('beta-staging',
                              'http://beta-staging.example.org',
                              '137ab30624237b6444b8c62a')
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'devel',
                          'local',
                          'beta-staging'])
        self.assertEqual(credentials.fetch_key('production'),
                         ('http://prod.example.org',
                          '37b6444b8c62a137ab306242'))
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel.example.org',
                          '137ab30624237b6444b8c62a'))
        self.assertEqual(credentials.fetch_key('local'),
                         ('http://127.0.0.1:8080',
                          'b8c62624237b6444137ab30'))
        self.assertEqual(credentials.fetch_key('beta-staging'),
                         ('http://beta-staging.example.org',
                          '137ab30624237b6444b8c62a'))

    def test_remove_key(self):
        """
        Credentials.remove_key: removes key from key file
        """
        tmp_key_file = self._make_key_file()
        credentials = Credentials(key_file=tmp_key_file)
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'devel',
                          'local'])
        credentials.remove_key('devel')
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'local'])
        self.assertEqual(credentials.fetch_key('production'),
                         ('http://prod.example.org',
                          '37b6444b8c62a137ab306242'))
        self.assertEqual(credentials.fetch_key('local'),
                         ('http://127.0.0.1:8080',
                          'b8c62624237b6444137ab30'))
        credentials.remove_key('nonexistent')
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'local'])
        self.assertEqual(credentials.fetch_key('production'),
                         ('http://prod.example.org',
                          '37b6444b8c62a137ab306242'))
        self.assertEqual(credentials.fetch_key('local'),
                         ('http://127.0.0.1:8080',
                          'b8c62624237b6444137ab30'))

    def test_update_key(self):
        """
        Credentials.update_key: updates details in key file
        """
        tmp_key_file = self._make_key_file()
        credentials = Credentials(key_file=tmp_key_file)
        self.assertEqual(credentials.list_keys(),
                         ['production',
                          'devel',
                          'local'])
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel.example.org',
                          '137ab30624237b6444b8c62a'))
        credentials.update_key('devel')
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel.example.org',
                          '137ab30624237b6444b8c62a'))
        credentials.update_key('devel',
                               new_url='http://devel2.example.org')
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel2.example.org',
                          '137ab30624237b6444b8c62a'))
        credentials.update_key('devel',
                               new_api_key='eadef00d245c3d0135ba9ccae7e77aef')
        self.assertEqual(credentials.fetch_key('devel'),
                         ('http://devel2.example.org',
                          'eadef00d245c3d0135ba9ccae7e77aef'))
        credentials.update_key('devel',
                               new_url='http://devel.example.org',
                               new_api_key='137ab30624237b6444b8c62a')
