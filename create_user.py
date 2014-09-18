#!/bin/env python
#
# Create a new user
import sys
import re
import getpass
import optparse
from bioblend import galaxy

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
        if not re.match("^[a-z0-9\-]+$",name):
            sys.stderr.write("Invalid name: must contain only lower-case letters, "
                             "numbers and '-'\n")
            sys.exit(1)
    except IndexError:
        # No public name supplied, make from email address
        name = email.split('@')[0].lower().replace('.','-').replace('_','-')

    print "Create new user in Galaxy instance at %s" % galaxy_url
    print "Email : %s" % email
    print "Name  : %s" % name

    # Set up galaxy instance and check that email/name are not already in use
    gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)

    for user in galaxy.users.UserClient(gi).get_users():
        if user['email'] == email:
            sys.stderr.write("User with email '%s' already exists\n" % email)
            sys.exit(1)
        elif galaxy.users.UserClient(gi).show_user(user['id'])['username'] == name:
            sys.stderr.write("User with name '%s' already exists\n" % name)
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
    try:
        galaxy.users.UserClient(gi).create_local_user(email,name,passwd)
    except galaxy.client.ConnectionError,ex:
        print "Failed to create user:"
        print ex
        sys.exit(1)
    print "Done"
    
