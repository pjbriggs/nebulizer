#!/usr/bin/env python
#
# users: functions for managing users
import sys
import re
import getpass
import fnmatch
from bioblend import galaxy
from mako.template import Template

# Classes

class User:
    """
    Class wrapping extraction of user data

    Provides an interface for accessing data about a user
    in a Galaxy instance, which has been retrieved via a
    a call to the Galaxy API using bioblend.

    """
    def __init__(self,user_data):
        """
        Create a new User instance

        ``user_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for user_data in galaxy.users.UserClient(gi).get_users():
        >>>    print User(user_data).name

        """
        self.email = user_data['email']
        self.username = user_data['username']
        self.id = user_data['id']

# Functions

def get_users(gi):
    """
    Return list of users in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of User objects.

    """
    users = []
    user_client = galaxy.users.UserClient(gi)
    for user_data in user_client.get_users():
        users.append(User(user_data))
    return users

def list_users(gi,name=None):
    """
    List users in Galaxy instance

    Arguments:
      gi    : Galaxy instance
      name  : optionally, only list matching emails/usernames

    """
    users = get_users(gi)
    if name:
        name = name.lower()
        users = filter(lambda u: fnmatch.fnmatch(u.username.lower(),name) or
                       fnmatch.fnmatch(u.email.lower(),name),users)
    for user in users:
        print "%s\t%s\t%s" % (user.email,
                              user.username,
                              user.id)

def create_user(gi,email,username=None,passwd=None,only_check=False,
                mako_template=None):
    """
    Create a new Galaxy user

    Attempts to create a single user in a Galaxy instance with the
    supplied credentials.

    Arguments:
      gi    : Galaxy instance
      email : email address for the new user
      username: (optional) name to associate with the user. If
        'None' then will be generated from the email address.
      passwd: (optional) password for the new user. If 'None' then
        the user will be prompted to supply a password.
      only_check: if True then only run the checks, don't try to
        make the user on the system.
      mako_template (optional): Mako template that will be populated
        and printed

    Returns:
      0 on success, 1 on failure.

    """
    # Check if user already exists
    if not check_new_user_info(gi,email,username):
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
    try:
        galaxy.users.UserClient(gi).create_local_user(username,
                                                      email,passwd)
    except galaxy.client.ConnectionError,ex:
        print "Failed to create user:"
        print ex
        return 1
    print "Created new account for %s" % email
    if mako_template:
        print render_mako_template(mako_template,email,passwd)
    return 0

def create_users_from_template(gi,template,start,end,passwd=None,
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
      gi       : Galaxy instance
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
    # Deal with password
    if passwd is not None:
        if not validate_password(passwd):
            sys.stderr.write("Invalid password\n")
            return 1
    else:
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
        name = get_username_from_login(email)
        ##print "%s, %s" % (email,name)
        if not check_new_user_info(gi,email,name):
            return 1
    if only_check:
        print "All emails and usernames ok: not currently in use"
        return 0
    # Make the accounts
    for email in emails:
        name = get_username_from_login(email)
        print "Email : %s" % email
        print "Name  : %s" % name
        if create_user(gi,email,name,passwd):
            return 1
    return 0

def create_batch_of_users(gi,tsv,only_check=False,mako_template=None):
    """
    Create a batch of users in Galaxy from a list in a TSV file

    Attempts to create multiple users in a Galaxy instance, using
    a list of email addresses, passwords and (optionally) names
    supplied via a TSV file.

    The file should consist of lines of the form e.g.:

    a.user@galaxy.ac.uk	p@ssw0rd	a-user

    The last value (the public name) can be missing, in which case
    the name will be generated from the email address.

    If an email address is already used for an account in the
    target Galaxy instance then it will be skipped.

    Blank lines and lines starting with '#' are ignored.

    Arguments:
      gi : Galaxy instance
      tsv: Name of TSV file to read user data from
      only_check: if True then only run the checks, don't try to
        make the users on the system.
      mako_template (optional): Mako template that will be populated
        and printed

    Returns:
      0 on success, 1 on failure.
    
    """
    # Open file
    print "Reading data from file '%s'" % tsv
    users = {}
    for line in open(tsv,'r'):
        # Skip blank or comment lines
        if line.startswith('#') or not line.strip():
            continue
        # Extract data
        items = line.strip().split('\t')
        passwd = None
        name = None
        try:
            email = items[0].lower().strip()
            passwd = items[1].strip()
            name = items[2].strip()
        except IndexError:
            pass
        # Do checks
        if email in users:
            sys.stderr.write("%s: appears multiple times\n" % email)
            return 1
        if passwd is None:
            sys.stderr.write("%s: no password supplied\n" % email)
            return 1
        elif not validate_password(passwd):
            sys.stderr.write("%s: invalid password\n" % email)
            return 1
        if name is None:
            name = get_username_from_login(email)
        if check_new_user_info(gi,email,name):
            users[email] = { 'name': name, 'passwd': passwd }
            print "%s\t%s\t%s" % (email,'*****',name)
    if only_check:
        return 0
    # Make the accounts
    for email in users:
        name = users[email]['name']
        passwd = users[email]['passwd']
        if create_user(gi,email,name,passwd):
            return 1
        if mako_template:
            print render_mako_template(mako_template,email,passwd)
    return 0

def check_new_user_info(gi,email,username):
    """
    Check if username or login are already in use

    """
    lookup_user = filter(lambda u: u.email == email or
                         u.username == username,get_users(gi))
    if lookup_user:
        sys.stderr.write("User details clash with existing user(s):\n")
        for user in lookup_user:
            sys.stderr.write("%s\n" % '\t'.join(user.email,
                                                user.username)) 
        return False
    return True

def check_username_format(username):
    """
    Check that format of 'username' is valid

    """
    return bool(re.match(r"^[a-z0-9\-]+$",username))

def get_username_from_login(email):
    """
    Create a public user name from an email address

    """
    return str(email).split('@')[0].lower().replace('.','-').replace('_','-')

def validate_password(passwd):
    """
    Check if password format is valid

    """
    if len(passwd) < 6:
        return False
    return True

def get_passwd():
    """Prompt user for a password

    Prompts user to enter and confirm a password. Raises an exception
    if the password is deemed to be invalid (e.g. too short), or if
    the password confirmation fails.

    Returns:
      Password string entered by the user.

    """
    passwd = getpass.getpass("Enter password for new user: ")
    if not validate_password(passwd):
        raise Exception("Invalid password: must be 6 or more characters")
    passwd2 = getpass.getpass("Confirm password: ")
    if passwd2 != passwd:
        raise Exception("Passwords don't match")
    return passwd

def render_mako_template(filename,email,password=None):
    """Render Mako template

    Render a Mako template from a file. The following variables are
    supplied to the template:

    first_name
    email
    password

    """
    first_name = email.split('.')[0].title()
    return Template(filename=filename).render(first_name=first_name,
                                              email=email,
                                              password=password)
