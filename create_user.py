#!/bin/env python
#
# Create a new user
import sys
import re
import getpass
import optparse
import nebulizer

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
        if not nebulizer.check_username_format(name):
            sys.stderr.write("Invalid name: must contain only lower-case letters, "
                             "numbers and '-'\n")
            sys.exit(1)
    except IndexError:
        # No public name supplied, make from email address
        name = nebulizer.get_username_from_login(email)

    print "Create new user in Galaxy instance at %s" % galaxy_url
    print "Email : %s" % email
    print "Name  : %s" % name

    # Set up galaxy instance and check that email/name are not already in use
    ni = nebulizer.Nebulizer(galaxy_url,api_key)
    if not ni.check_new_user_info(email,name):
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
    if not ni.create_user(email,name,passwd):
        sys.exit(1)
    print "Done"
    
