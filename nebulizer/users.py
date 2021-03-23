#!/usr/bin/env python
#
# users: functions for managing users
import logging
import re
import getpass
import fnmatch
from bioblend import galaxy
from bioblend import ConnectionError
from mako.template import Template
from .core import get_galaxy_config
from .core import prompt_for_confirmation
from .core import Reporter

# Logging
logger = logging.getLogger(__name__)

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
        >>>    print(User(user_data).name)

        """
        # Initialise
        self.email = user_data['email']
        self.username = user_data['username']
        self.id = user_data['id']
        self.quota = None
        self.quota_percent = None
        self.total_disk_usage = None
        self.nice_total_disk_usage = None
        self.is_admin = None
        self.active = None
        self.deleted = None
        self.purged = None
        self.preferences = None
        # Populate with additional data items
        self.update(user_data)

    def update(self,user_data):
        """
        Update the data items associated with the user

        ``user_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> user.update(galaxy.users.UserClient(gi).show_user(user.id))

        """
        # Check this is the same user ID
        if user_data['id'] != self.id:
            raise Exception("Tried to update data for user ID '%s' "
                            "with data for user ID '%s'" %
                            (self.id,
                             user_data['id']))
        # Update the attributes
        for attr in user_data.keys():
            try:
                setattr(self,attr,user_data[attr])
            except AttributeError:
                pass

    @property
    def display_status(self):
        """
        Return status based on the user data

        Status will be returned as one of:

        - active
        - deleted
        - purged

        or an empty string, depending on the `purged`,
        `deleted` and `active` flag.
        """
        if self.purged:
            return 'purged'
        elif self.deleted:
            return 'deleted'
        elif self.active:
            return 'active'
        else:
            return ''

    @property
    def display_quota_percent(self):
        """
        Return quota percentage for display

        Percentage will be 'n/a' for unlimited
        quotas, or a value with a percentage
        symbol for real quotas.
        """
        if self.quota == 'unlimited':
            return 'n/a'
        elif self.quota_percent:
            return "%s%%" % self.quota_percent
        else:
            return "0%"

    def sort_key(self,*keys):
        """
        Return 'sort key' based on specified keys

        Given one or more keys, returns a tuple
        with the values for each of those keys
        for this user (in the specified order),
        which can then be used in
        sorting operations.

        Valid keys are:

        - email (normalised email address)
        - disk_usage (amount of disk space used)
        - quota (total quota allowance)
        - quota_usage (percentage of quota used)

        """
        keys = list(keys)
        if 'email' not in keys:
            keys.append('email')
        sort_key = []
        for key in keys:
            if key == 'email':
                # Normalised email address
                sort_key.append(
                    self.email.lower()
                    if not (self.purged and '@' not in self.email) else '')
            elif key == 'disk_usage':
                # Disk usage (high to low)
                sort_key.append(-self.total_disk_usage)
            elif key == 'quota':
                # Quota allowance (high to low)
                if self.quota:
                    # Quota is defined, convert from 'nice'
                    # format to a float
                    if self.quota.endswith('KB'):
                        quota = float(self.quota[:-2])*1024
                    elif self.quota.endswith('GB'):
                        quota = float(self.quota[:-2])*(1024**2)
                    elif self.quota.endswith('TB'):
                        quota = float(self.quota[:-2])*(1024**3)
                    elif self.quota == 'unlimited':
                        # Special case: try and make 'unlimited'
                        # bigger than any other value
                        quota = 1024.0**6
                    else:
                        # Assume it's bytes
                        quota = float(self.quota)
                else:
                    # No quota defined so set to zero
                    quota = 0.0
                sort_key.append(-quota)
            elif key == 'quota_usage':
                # Percentage of quota used (high to low)
                if self.quota_percent:
                    # Quota percentage is defined
                    if self.quota == 'unlimited':
                        # Special case: set 'unlimited' to
                        # zero
                        quota_usage = 0.0
                    else:
                        # Use as-is
                        quota_usage = -self.quota_percent
                else:
                    # No quota percentage defined, so
                    # set to zero
                    quota_usage = 0.0
                sort_key.append(quota_usage)
            else:
                raise KeyError("Unknown sort key: '%s'" % key)
        return tuple(sort_key)

# Functions

def get_users(gi,status='active'):
    """
    Return list of users in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      status (bool): only return users with the matching
        status ('active', 'deleted', 'purged' or 'all')

    Returns:
      list: list of User objects.

    """
    users = []
    user_client = galaxy.users.UserClient(gi)
    # Get active users
    if status in ('active','all'):
        for user_data in user_client.get_users():
            user = User(user_data)
            user.update(galaxy.users.UserClient(gi).show_user(user.id))
            users.append(user)
    # Get deleted and purged users
    if status in ('deleted','purged','all'):
        keep_deleted = status in ('deleted','all')
        keep_purged = status in ('purged','all')
        for user_data in user_client.get_users(deleted=True):
            user = User(user_data)
            user.update(galaxy.users.UserClient(gi).show_user(
                user.id,
                deleted=True))
            if (user.purged and keep_purged) or \
               (not user.purged and keep_deleted):
                users.append(user)
    return users

def get_user(gi,email):
    """
    Get the user data corresponding to a username email

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      email : email address for the user

    Returns:
      User: 'User' instance, or None if no match.
    """
    try:
        for u in get_users(gi,status='all'):
            if fnmatch.fnmatch(u.email,email):
                return u
    except ConnectionError as ex:
        logger.warning("Failed to get user list: {} ({})".format(ex.body,
                                                             ex.status_code))
    return None

def get_user_id(gi,email):
    """
    Get the user ID corresponding to a username email

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      email : email address for the user

    Returns:
      String: user ID, or None if no match.
    """
    try:
        return get_user(gi,email).id
    except AttributeError:
        return None

def list_users(gi,name=None,long_listing_format=False,status='active',
               sort_by=None,show_id=False):
    """
    List users in Galaxy instance

    Arguments:
      gi    : Galaxy instance
      name  : optionally, only list matching emails/usernames
      long_listing_format (boolean): if True then use a
        long listing format when reporting items
      status (str): list users with matching status: 'active'
        (default), 'deleted', or 'purged'. Use 'all' to list
        all accounts regardless of status
      sort_by (list): list of fields to sort users into order
        on this field (default sorting is done on user email)
      show_id (bool): if True then report user's Galaxy ID

    """
    # Get user data
    try:
        users = get_users(gi,status=status)
    except ConnectionError as ex:
        logger.fatal("Failed to get user list: {} ({})".format(ex.body,
                                                           ex.status_code))
        return 1
    # Get Galaxy config data to determine if quotas are enabled
    # (if not then don't report quota percentage in long format)
    if long_listing_format:
        config = get_galaxy_config(gi)
        enable_quotas = config['enable_quotas']
    else:
        enable_quotas = False
    # Filter user list on supplied name
    if name:
        name = name.lower()
        users = [u for u in users if
                 (fnmatch.fnmatch(u.username.lower(),name) or
                  fnmatch.fnmatch(u.email.lower(),name))]
    # Sort into order
    if not sort_by:
        sort_by = ()
    users.sort(key=lambda u: u.sort_key(*sort_by))
    # Report users
    output = Reporter()
    for user in users:
        # Collect data items to report
        if user.purged and '@' not in user.email:
            display_items = ['<purged>','<purged>']
        else:
            display_items = [user.email,user.username]
        if long_listing_format:
            # Long listing format includes:
            # - disk usage
            # - quota size (if quotas enabled)
            # - % quota used (if quotas enabled)
            # - if account status ('active','deleted' etc)
            # - if user is an admin
            display_items.append(user.nice_total_disk_usage)
            if enable_quotas:
                display_items.extend([user.quota,
                                      user.display_quota_percent])
            display_items.extend([user.display_status,
                                  'admin' if user.is_admin else ''])
        if show_id:
            # Also report the internal user ID
            display_items.append(user.id)
        output.append(display_items)
    # Report user data
    output.report()
    print("total %s" % len(users))

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
        print("Email and username ok: not currently in use")
        return 0
    # Prompt for password
    if passwd is None:
        try:
            passwd = get_passwd()
        except Exception as ex:
            logger.error("%s" % ex)
            return 1
    # Create the new user
    try:
        galaxy.users.UserClient(gi).create_local_user(username,
                                                      email,passwd)
    except galaxy.client.ConnectionError as ex:
        print("Failed to create user:")
        print(ex)
        return 1
    print("Created new account for %s" % email)
    if mako_template:
        print(render_mako_template(mako_template,email,passwd))
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
        logger.error("Incorrect email template format")
        return 1
    # Deal with password
    if passwd is not None:
        if not validate_password(passwd):
            logger.error("Invalid password")
            return 1
    else:
        try:
            passwd = get_passwd()
        except Exception as ex:
            logger.error("%s" % ex)
            return 1
    # Generate emails
    emails = [template.replace('#',str(i)) for i in range(start,end+1)]
    # Check that these are available
    print("Checking availability")
    for email in emails:
        name = get_username_from_login(email)
        ##print("%s, %s" % (email,name))
        if not check_new_user_info(gi,email,name):
            return 1
    if only_check:
        print("All emails and usernames ok: not currently in use")
        return 0
    # Make the accounts
    for email in emails:
        name = get_username_from_login(email)
        print("Email : %s" % email)
        print("Name  : %s" % name)
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
    print("Reading data from file '%s'" % tsv)
    users = {}
    for line in open(tsv):
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
            logger.error("%s: appears multiple times" % email)
            return 1
        if passwd is None:
            logger.error("%s: no password supplied" % email)
            return 1
        elif not validate_password(passwd):
            logger.error("%s: invalid password\n" % email)
            return 1
        if name is None:
            name = get_username_from_login(email)
        if check_new_user_info(gi,email,name):
            users[email] = { 'name': name, 'passwd': passwd }
            print("{}\t{}\t{}".format(email,'*****',name))
    if only_check:
        return 0
    # Make the accounts
    for email in users:
        name = users[email]['name']
        passwd = users[email]['passwd']
        if create_user(gi,email,name,passwd):
            return 1
        if mako_template:
            print(render_mako_template(mako_template,email,passwd))
    return 0

def delete_user(gi,email,purge=False,no_confirm=False):
    """
    Delete a user account from a Galaxy instance

    Arguments:
      gi         : Galaxy instance
      email      : email address of user to delete
      purge      : if True then also purge the user
      no_confirm : if True then don't prompt to confirm the
        deletion operation

    Returns:
      0 on success, 1 on failure.

    """
    # Get the data for the supplied user
    user = get_user(gi,email)
    if user is None:
        logger.fatal("No user '%s'" % email)
        return 1
    # Is user already deleted or purged?
    if user.purged:
        logger.fatal("'%s': already deleted and purged" % email)
        return 0
    elif user.deleted and not purge:
        logger.fatal("'%s': already deleted (but you can rerun with "
                     "--purge)" % email)
        return 0
    # Prompt user for confirmation
    if not user.deleted:
        prompt = "Delete {}user '{}'?".format("& purge " if purge else '',
                                          email)
    else:
        prompt = "Purge deleted user '{}'?".format(email)
    if no_confirm or prompt_for_confirmation(prompt,default="n"):
        try:
            if not user.deleted:
                # Need to delete first
                galaxy.users.UserClient(gi).delete_user(user.id)
            if purge:
                # Can only purge a deleted user
                galaxy.users.UserClient(gi).delete_user(user.id,purge=True)
            print("Deleted {}user '{}'".format("& purged " if purge else '',
                                           email))
            return 0
        except ConnectionError as ex:
            logger.fatal("Failed to delete user: {} ({})".format(ex.body,
                                                             ex.status_code))
            return 1
    else:
        print("User '%s' not deleted and/or purged" % email)
        return 0

def check_new_user_info(gi,email,username):
    """
    Check if username or login are already in use

    """
    lookup_user = [u for u in get_users(gi)
                   if u.email == email or u.username == username]
    if lookup_user:
        error_msg = "User details clash with existing user(s):"
        for user in lookup_user:
            error_msg += "\n%s" % ('\t'.join([user.email,
                                             user.username]))
        logger.error(error_msg)
        return False
    return True

def get_user_api_key(gi,username=None):
    """
    Retrieve an API key for a user

    Arguments:
      username (str): email address or username for the
        user to get the API key for; default is to get
        the key for the current user

    """
    if username is None:
        # Fetch the details for the current user
        try:
            user = galaxy.users.UserClient(gi).get_current_user()
            print("Username: %s" % username)
        except galaxy.client.ConnectionError:
            logger.error("Cannot determine user associated with "
                          "this instance")
            return
        except AttributeError:
            logger.error("Unable to fetch user associated with "
                         "this instance")
            return
    else:
        # Fetch the details for the specified user
        user = None
        for u in get_users(gi):
            if (u.email == username) or (u.username == username):
                user = u
                break
    if user is None:
        logger.error("Cannot get info for user '%s'\n" % username)
        return
    # Get the API key
    user_id = user.id
    try:
        api_key = galaxy.users.UserClient(gi).create_user_apikey(user_id)
    except galaxy.client.ConnectionError as ex:
        print("Failed to fetch API key for user '%s': " % username)
        print(ex)
        return
    return api_key

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
