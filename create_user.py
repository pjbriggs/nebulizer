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

__version__ = '0.0.2'

def get_passwd():
    """Prompt user for a password

    Prompts user to enter and confirm a password. Raises an exception
    if the password is deemed to be invalid (e.g. too short), or if
    the password confirmation fails.

    Returns:
      Password string entered by the user.

    """
    passwd = getpass.getpass("Enter password for new user: ")
    if len(passwd) < 6:
        raise Exception("Invalid password: must be 6 or more characters")
    passwd2 = getpass.getpass("Confirm password: ")
    if passwd2 != passwd:
        raise Exception("Passwords don't match")
    return passwd

def create_user(ni,email,name=None,passwd=None,only_check=False):
    """Creates a new Galaxy user

    Attempts to create a single user in a Galaxy instance with the
    supplied credentials.

    Arguments:
      ni    : Nebulizer instance associated with a Galaxy instance
      email : email address for the new user
      name  : (optional) name to associate with the user. If
        'None' then will be generated from the email address.
      passwd: (optional) password for the new user. If 'None' then
        the user will be prompted to supply a password.
      only_check: if True then only run the checks, don't try to
        make the user on the system.

    Returns:
      0 on success, 1 on failure.

    """
    # Check if user already exists
    if not ni.check_new_user_info(email,name):
        return 1
    if only_check:
        print "Email and username ok: not currently in use"
        return 0
    # Prompt for password
    if passwd is None:
        try:
            passwd = get_passwd()
        except Exception, ex:
            sys.stderr.write("%s\n" % ex)
            return 1
    # Create the new user
    if not ni.create_user(email,name,passwd):
        return 1
    print "Created new account for %s" % email
    return 0

def create_users_from_template(ni,template,start,end,passwd=None,
                               only_check=False):
    """
    Create a batch of users in Galaxy, based on template email

    Attempts to create multiple users in a Galaxy instance, using
    a template email address and a range of integer indices to
    generate the names.

    'template' should include a '#' symbol indicating where an integer
    index should be substituted (e.g. 'student#@galaxy.ac.uk').
    'start' and 'end' are the range of ids to create (e.g. 1 to 10).

    All accounts will be created with the same password; names will
    be generated automatically from the email addresses

    For example: the template 'student#@galaxy.ac.uk' with a range of
    1 to 5 will generate:

    student1@galaxy.ac.uk
    student2@galaxy.ac.uk
    ...
    student5@galaxy.ac.uk

    Arguments:
      ni       : Nebulizer instance associated with a Galaxy instance
      template : template email address for the batch of new users
      start    : initial integer index for user names
      end      : final integer index for user names
      passwd   : (optional) password for the new user. If 'None' then
        the user will be prompted to supply a password.
      only_check: if True then only run the checks, don't try to
        make the users on the system.

    Returns:
      0 on success, 1 on failure.
    
    """
    # Check template
    name,domain = template.split('@')
    if name.count('#') != 1 or domain.count('#') != 0:
        sys.stderr.write("Incorrect email template format\n")
        return 1
    # Prompt for password
    if passwd is None:
        try:
            passwd = get_passwd()
        except Exception, ex:
            sys.stderr.write("%s\n" % ex)
            return 1
    # Generate emails
    emails = [template.replace('#',str(i)) for i in range(start,end+1)]
    # Check that these are available
    print "Checking availability"
    for email in emails:
        name = nebulizer.get_username_from_login(email)
        ##print "%s, %s" % (email,name)
        if not ni.check_new_user_info(email,name):
            return 1
    if only_check:
        print "All emails and usernames ok: not currently in use"
        return 0
    # Make the accounts
    for email in emails:
        name = nebulizer.get_username_from_login(email)
        print "Email : %s" % email
        print "Name  : %s" % name
        if not ni.create_user(email,name,passwd):
            return 1
        print "Created new account for %s" % email
    return 0

if __name__ == "__main__":
    # Collect arguments
    p = optparse.OptionParser(usage="\n%prog options GALAXY_URL API_KEY EMAIL [PUBLIC_NAME]",
                              version="%%prog %s" % __version__,
                              description="Create new user(s) in the specified Galaxy "
                              "instance.")
    p.add_option('-p','--password',action='store',dest='passwd',default=None,
                 help="specify password for new user account (otherwise program will "
                 "prompt for password)")
    p.add_option('-c','--check',action='store_true',dest='check',default=False,
                 help="check user details but don't try to create the new account")
    p.add_option('-t','--template',action='store_true',dest='template',default=False,
                 help="indicates that EMAIL is actually a 'template' email address which "
                 "includes a '#' symbol as a placeholder where an integer index should be "
                 "substituted to make multiple accounts (e.g. 'student#@galaxy.ac.uk'). "
                 "The --range option supplies the range of integer indices.")
    p.add_option('-r','--range',action='store',dest='range',default=None,
                 help="RANGE defines a set of integer indices to use when the --template "
                 "option is specified. RANGE is of the form 'START[,END]' e.g. '1', '20,25'")
    options,args = p.parse_args()
    if len(args) < 3 or len(args) > 4:
        p.error("Wrong arguments")
    galaxy_url = args[0]
    api_key = args[1]
    email = args[2]
    passwd = options.passwd

    # Set up Nebulizer instance to interact with Galaxy
    ni = nebulizer.Nebulizer(galaxy_url,api_key)

    # Determine mode of operation
    print "Create new users in Galaxy instance at %s" % galaxy_url
    if options.template:
        # Get the range of integer indices
        if options.range is None:
            sys.stderr.write("No range: use --range to specify start and end ID indices\n")
            sys.exit(1)
        start = int(options.range.split(',')[0])
        try:
            end = int(options.range.split(',')[1])
        except IndexError:
            end = start
        # Create users
        retval = create_users_from_template(ni,email,start,end,passwd,
                                            only_check=options.check)
    else:
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
        # Create user
        print "Email : %s" % email
        print "Name  : %s" % name
        retval = create_user(ni,email,name,passwd,
                             only_check=options.check)

    # Finished
    sys.exit(retval)
    
