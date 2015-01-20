#!/bin/env python
#
# Create a new user
import sys
import re
import getpass
import optparse
from bioblend import galaxy

class GalaxyInstance:

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
    return bool(re.match("^[a-z0-9\-]+$",name))

def get_username_from_login(email):
    """Create a public user name from an email address

    """
    return str(email).split('@')[0].lower().replace('.','-').replace('_','-')

if __name__ == "__main__":
    # Collect arguments
    p = optparse.OptionParser(usage="%prog GALAXY_URL API_KEY EMAIL [PUBLIC_NAME]",
                              description="Create a new user in the specified Galaxy "
                              "instance")
    options,args = p.parse_args()
    if len(args) < 3 or len(args) > 4:
        p.error("Wrong arguments")
    galaxy_url = args[0]
    api_key = args[1]
    email = args[2]

    # Collect public name
    try:
        name = args[3]
        if not check_username_format(name):
            sys.stderr.write("Invalid name: must contain only lower-case letters, "
                             "numbers and '-'\n")
            sys.exit(1)
    except IndexError:
        # No public name supplied, make from email address
        name = get_username_from_login(email)

    print "Create new user in Galaxy instance at %s" % galaxy_url
    print "Email : %s" % email
    print "Name  : %s" % name

    # Set up galaxy instance and check that email/name are not already in use
    gi = GalaxyInstance(galaxy_url,api_key)
    if not gi.check_new_user_info(email,name):
        sys.exit(1)

    # Prompt for password
    passwd = getpass.getpass("Enter password for new user: ")
    if len(passwd) < 6:
        sys.stderr.write("Invalid password: must be 6 or more characters\n")
        sys.exit(1)
    passwd2 = getpass.getpass("Confirm password: ")
    if passwd2 != passwd:
        sys.stderr.write("Passwords don't match\n")
        sys.exit(1)

    # Create the new user
    if not gi.create_user(email,name,passwd):
        sys.exit(1)
    print "Done"
    
