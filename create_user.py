#!/bin/env python
#
# Create new user accounts in a Galaxy instance
import sys
import getpass
import optparse
import nebulizer

"""
create_user.py

"""

__version__ = '0.0.1'

if __name__ == "__main__":
    # Collect arguments
    p = optparse.OptionParser(usage="%prog options GALAXY_URL API_KEY EMAIL [PUBLIC_NAME]",
                              version="%%prog %s" % __version__,
                              description="Create new user(s) in the specified Galaxy "
                              "instance")
    p.add_option('-p','--password',action='store',dest='passwd',default=None,
                 help="specify password for new user account (otherwise program will "
                 "prompt for password")
    p.add_option('-c','--check',action='store_true',dest='check',default=False,
                 help="check user details but don't try to create the new account")
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
    if options.check:
        print "Email and username ok: not currently in use"
        sys.exit(0)

    # Prompt for password
    passwd = options.passwd
    if passwd is None:
        passwd = getpass.getpass("Enter password for new user: ")
    if len(passwd) < 6:
        sys.stderr.write("Invalid password: must be 6 or more characters\n")
        sys.exit(1)
    if options.passwd is None:
        passwd2 = getpass.getpass("Confirm password: ")
        if passwd2 != passwd:
            sys.stderr.write("Passwords don't match\n")
            sys.exit(1)

    # Create the new user
    if not ni.create_user(email,name,passwd):
        sys.exit(1)
    print "Created new account for %s" % email
    
