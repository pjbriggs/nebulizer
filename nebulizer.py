#!/bin/env python
#
# nebulizer: Python lib for Galaxy bootstrapping functionality

import sys
import re
from bioblend import galaxy

class Nebulizer:
    """Class wrapping functionality from bioblend
    """

    def __init__(self,galaxy_url,api_key):
        self._gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)

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
