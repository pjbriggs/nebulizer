#!/usr/bin/env python
#
# nebulizer: Python lib for Galaxy bootstrapping functionality

import sys
import os
import re
from bioblend import galaxy

class Credentials:
    """Class for managing credentials for Galaxy instances

    Credentials for different galaxy instances can be
    stored in a file under $HOME/.nebulizer

    Entries in the file consist of lines with three tab
    separated values:

    ALIAS   URL    API_KEY

    Blank lines or lines starting '#' are skipped.

    """

    def __init__(self):
        self._key_file = os.path.join(os.path.expanduser("~"),
                                           '.nebulizer')

    def store_key(self,name,url,api_key):
        """Store a Galaxy API key

        Appends an entry to the key file.

        """
        with open(self._key_file,'w+') as fp:
            fp.write("%s\t%s\t%s\n" % (name,url,api_key))

    def fetch_key(self,name):
        """Fetch credentials associated with a Galaxy instance

        Looks up the credentials associated with the
        alias 'name', and returns the tuple:

        (GALAXY_URL,API_KEY)

        Raises a KeyError if no matching alias is found.

        """
        if os.path.exists(self._key_file):
            with open(self._key_file,'r') as fp:
                for line in fp:
                    if line.startswith('#') or not line.strip():
                        continue
                    alias,url,api_key = line.strip().split('\t')
                    if alias == name:
                        return (url,api_key)
        raise KeyError("'%s': not found" % name)

class Nebulizer:
    """Class wrapping functionality from bioblend
    """

    def __init__(self,galaxy_url,api_key=None):
        if api_key is None:
            galaxy_url,api_key = Credentials().fetch_key(galaxy_url)
        self._galaxy_url = galaxy_url
        self._gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)

    @property
    def galaxy_url(self):
        return self._galaxy_url

    def create_user(self,email,username,passwd):
        """Create a new user account with the specified credentials
        
        """
        try:
            galaxy.users.UserClient(self._gi).create_local_user(username,email,passwd)
            return True
        except galaxy.client.ConnectionError,ex:
            print "Failed to create user:"
            print ex
            return False

    def check_new_user_info(self,email,username):
        """Check if username or login are already in use

        """
        for user in galaxy.users.UserClient(self._gi).get_users():
            if user['email'] == email:
                sys.stderr.write("User with email '%s' already exists\n" % email)
                return False
            elif galaxy.users.UserClient(self._gi).show_user(user['id'])['username'] == username:
                sys.stderr.write("User with name '%s' already exists\n" % username)
                return False
        return True

def check_username_format(username):
    """Check that format of 'username' is valid

    """
    return bool(re.match("^[a-z0-9\-]+$",username))

def get_username_from_login(email):
    """Create a public user name from an email address

    """
    return str(email).split('@')[0].lower().replace('.','-').replace('_','-')

def validate_password(passwd):
    """Check if password format is valid

    """
    if len(passwd) < 6:
        return False
    return True
