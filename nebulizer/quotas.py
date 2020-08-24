#!/usr/bin/env python
#
# quotas: functions for managing quotas
import logging
import fnmatch
from bioblend import galaxy
from bioblend import ConnectionError
from .core import Reporter
from .core import prompt_for_confirmation
from .users import User
from .users import get_users
from .groups import Group
from .groups import get_groups

# Logging
logger = logging.getLogger(__name__)

# Constants
VALID_DEFAULTS = ('registered',
                  'unregistered',
                  'no')

# Classes

class Quota(object):
    """
    Class wrapping extraction of quota data

    Provides an interface for accessing data about a quota
    in a Galaxy instance, which has been retrieved via a
    a call to the Galaxy API using bioblend.

    """
    def __init__(self,quota_data):
        """
        Create a new Quota instance

        ``quota_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for data in galaxy.quotas.QuotaClient(gi).get_quotas():
        >>>    print(Quota(data).name)

        Data can be supplemented by calling the
        ``update`` method with another dictionary.

        """
        # Initialise
        self.id = quota_data['id']
        self.name = quota_data['name']
        self.bytes = None
        self.default = None
        self.description = None
        self.display_amount = None
        self.groups = None
        self.operation = None
        self.users = None
        self.deleted = None
        # Populate with additional data items
        self.update(quota_data)

    @property
    def default_for(self):
        """
        Returns class of user that quota is default for

        Will be 'registered', 'unregistered' or None.
        """
        if self.default:
            return self.default[0]['type']
        return None

    @property
    def list_users(self):
        """
        Returns list of associated User instances
        """
        if self.users:
            return [User(u['user']) for u in self.users]
        return []

    @property
    def list_groups(self):
        """
        Returns list of associated Group instances
        """
        if self.groups:
            return [Group(g['group']) for g in self.groups]
        return []

    def update(self,quota_data):
        """
        Update the data items associated with the quota

        ``quota_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> user.update(galaxy.users.UserClient(gi).show_user(user.id))

        """
        # Check this is the same user ID
        if quota_data['id'] != self.id:
            raise Exception("Tried to update data for quota ID '%s' "
                            "with data for quota ID '%s'" %
                            (self.id,
                             quota_data['id']))
        # Update the attributes
        for attr in quota_data.keys():
            try:
                setattr(self,attr,quota_data[attr])
            except AttributeError:
                pass

# Functions

def handle_quota_spec(quota):
    """
    Process an arbitrary quota specification

    Given a quota specification as a string,
    returns the operation and amount.

    The specification must be of the form:

    [OPERATION]AMOUNT

    where OPERATION is one of '=','+' or '-'
    and defaults to '=' if not present.
    """
    # Valid operations
    valid_operations = ('=','+','-')
    # Get operation
    if quota[0] in valid_operations:
        operation = quota[0]
        amount = quota[1:]
    else:
        operation = '='
        amount = quota
    return (operation,amount)

def get_quotas(gi,status='active'):
    """
    Return list of quotas from a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of Quota objects.
      status (bool): only return quotas with the matching
        status ('active', 'deleted' or 'all')

    """
    quotas = []
    quota_client = galaxy.quotas.QuotaClient(gi)
    # Get active quotas
    if status in ('active','all'):
        for quota_data in quota_client.get_quotas():
            quota = Quota(quota_data)
            quota.update(quota_client.show_quota(quota.id))
            quotas.append(quota)
    # Get deleted quotas
    if status in ('deleted','all'):
        for quota_data in quota_client.get_quotas(deleted=True):
            quota = Quota(quota_data)
            quota.update(quota_client.show_quota(quota.id,
                                                 deleted=True))
            quota.deleted = True
            quotas.append(quota)
    return quotas

def list_quotas(gi,name=None,status='active',long_listing_format=False):
    """
    List quotas in Galaxy instance

    Arguments:
      gi    : Galaxy instance
      name  : optionally, only list matching quota names
      status (str): list quotas with matching status: 'active'
        (default) or 'deleted'. Use 'all' to list all quotas
        regardless of status
      long_listing_format (boolean): if True then use a
        long listing format when reporting items

    """
    # Get quota data
    try:
        quotas = get_quotas(gi,status=status)
    except ConnectionError as ex:
        logger.fatal("Failed to get quota list: %s (%s)" % (ex.body,
                                                            ex.status_code))
        return 1
    # Filter quota list on supplied name
    if name:
        name = name.lower()
        quotas = [q for q in quotas
                  if fnmatch.fnmatch(q.name.lower(),name)]
    # Sort into order
    quotas.sort(key=lambda q: q.name.lower())
    # Report quotas
    if not long_listing_format:
        output = Reporter()
        for quota in quotas:
            n_users = len(quota.list_users)
            n_groups = len(quota.list_groups)
            # Collect data items to report on a single line
            display_items = [quota.name,
                             "%s%s" % (quota.operation,
                                       quota.display_amount),
                             "%s" % quota.default_for
                             if quota.default_for else '',
                             "%s user%s" %
                             (n_users,'' if n_users == 1 else 's'),
                             "%s group%s" %
                             (n_groups,'' if n_groups == 1 else 's'),
                             "active" if not quota.deleted
                             else "deleted"]
            output.append(display_items)
        output.report()
    else:
        # Long listing format reports each quota in
        # a block
        for quota in quotas:
            n_users = len(quota.list_users)
            n_groups = len(quota.list_groups)
            print("Quota name : %s" % quota.name)
            print("Description: %s" % quota.description)
            print("Operation  : %s" % quota.operation)
            print("Amount     : %s" % quota.display_amount)
            print("Default    : %s" % (quota.default_for
                                       if quota.default_for else 'no'))
            print("Status     : %s" % ("active" if not quota.deleted
                                       else "deleted"))
            print("%s associated user%s" % (n_users,
                                            '' if n_users == 1 else 's'))
            for user in quota.list_users:
                print("- %s" % user.email)
            print("%s associated group%s" % (n_groups,
                                             '' if n_groups == 1 else 's'))
            for group in quota.list_groups:
                print("- %s" % group.name)
            print("")
    print("total %s" % len(quotas))

def create_quota(gi,name,description,amount,operation,default=None,
                 users=None,groups=None):
    """
    Create a new quota in a Galaxy instance

    Attempts to create a new quota with the supplied details.

    Arguments:
      gi: Galaxy instance
      name: name for the new quota
      description: description for the new quota
      amount: string specifying the size of the new quota
      operation: operation to use when applying the new
        quota (i.e. '=','+' or '-')
      default: optionally specify if the new quota will
        be the default for 'registered' or 'unregistered'
        users
      users: list of user emails to associate with the
        new quota
      groups: list of group names to associate with the
        new quota
    """
    # Check for existing quota name
    existing_quotas = [q for q in get_quotas(gi,status='all')
                       if q.name == name]
    if existing_quotas:
        logger.fatal("'%s': quota already exists with this name" %
                     name)
        return 1
    # Check for valid 'default' setting
    if default:
        if default not in VALID_DEFAULTS:
            logger.fatal("'%s': not a valid default (must be one of "
                         "%s)" % (default,
                                  ','.join(["'%s'" % d
                                            for d in VALID_DEFAULTS])))
            return 1
    else:
        default = 'no'
    # Sort out the users and groups
    if users:
        galaxy_users = [u.email for u in get_users(gi)]
        for user in users:
            # Check that user exists
            if user not in galaxy_users:
                logger.fatal("%s: user doesn't exist" % user)
                return 1
    if groups:
        galaxy_groups = [g.name for g in get_groups(gi)]
        for group in groups:
            # Check that the group exists
            if group not in galaxy_groups:
                logger.fatal("%s: group doesn't exist" % group)
                return 1
    # Create the new quota
    print("Quota name : %s" % name)
    print("Description: %s" % description)
    print("Operation  : %s" % operation)
    print("Amount     : %s" % amount)
    print("Default    : %s" % default)
    if users:
        print("Users:")
        for user in users:
            print("-- %s" % user)
    if groups:
        print("Groups:")
        for group in groups:
            print("-- %s" % group)
    try:
        quota_client = galaxy.quotas.QuotaClient(gi)
        result = quota_client.create_quota(name,
                                           description,
                                           amount,
                                           operation,
                                           default=default,
                                           in_users=users,
                                           in_groups=groups)
        print("%s" % result['message'])
        return 0
    except galaxy.client.ConnectionError as ex:
        logger.fatal("Failed to create quota:")
        logger.fatal(ex)
        return 1

def update_quota(gi,name,new_name=None,new_description=None,
                 new_amount=None,new_operation=None,
                 new_default=None,add_users=None,add_groups=None,
                 remove_users=None,remove_groups=None,
                 undelete=False):
    """
    Create a new quota in a Galaxy instance

    Attempts to create a new quota with the supplied details.

    Arguments:
      gi: Galaxy instance
      name: name of the quota to update
      new_name: new name for the quota
      new_description: new description for the quota
      new_amount: string specifying the new size of the quota
      new_operation: new operation to use when applying the
        quota (i.e. '=','+' or '-')
      new_default: whether the new quota will be the default
        for 'registered' or 'unregistered' users
      add_users: list of user emails to associate with the
        quota (in addition to any already associated)
      add_groups: list of group names to associate with the
        quota (in addition to any already associated)
      remove_users: list of user emails to disassociate from
        the quota
      remove_groups: list of group names to disassociate from
        the quota
      undelete: if True then restores deleted quota
    """
    # Get the current settings for the quota
    quota = [q for q in get_quotas(gi,status='all')
             if q.name == name]
    if len(quota) != 1:
        logger.fatal("'%s': no such quota?" % name)
        return 1
    quota = quota[0]
    # Check if deleted quota is being restored
    if quota.deleted and not undelete:
        logger.fatal("'%s': trying to modify a deleted quota"
                     % name)
        return 1
    # Set defaults
    name = None
    description = None
    amount = None
    operation = None
    default = None
    # Update the quota name
    if new_name:
        name = new_name
        print("Quota name : %s" % name)
    # Update the description
    if new_description:
        if not name:
            name = quota.name
        description = new_description
        print("Description: %s" % description)
    # Update the quota size
    if new_amount and new_operation:
        if new_amount:
            amount = new_amount
        else:
            amount = quota.display_amount
        if new_operation:
            operation = new_operation
        else:
            operation = quota.operation
        print("Operation  : %s" % operation)
        print("Amount     : %s" % amount)
    # Update the default class
    if new_default:
        default = new_default
        print("Default    : %s" % default)
    # Update the list of users
    users = None
    if add_users or remove_users:
        users = [u.email for u in quota.list_users]
        if add_users:
            galaxy_users = [u.email for u in get_users(gi)]
            for user in add_users:
                # Check that user exists
                if user not in galaxy_users:
                    logger.fatal("%s: user doesn't exist" % user)
                    return 1
                # Only add users that aren't already associated
                # with the quota
                if user not in users:
                    users.append(user)
        if remove_users:
            for user in remove_users:
                users = [u for u in users if u != user]
    # Update list of groups
    groups = None
    if add_groups or remove_groups:
        groups = [g.name for g in quota.list_groups]
        if add_groups:
            galaxy_groups = [g.name for g in get_groups(gi)]
            for group in add_groups:
                # Check that group exists
                if group not in galaxy_groups:
                    logger.fatal("%s: group doesn't exist" % group)
                    return 1
                # Only add groups that aren't already associated
                # with the quota
                if group not in groups:
                    groups.append(group)
        if remove_groups:
            for group in remove_groups:
                groups = [g for g in groups if g != group]
    try:
        quota_client = galaxy.quotas.QuotaClient(gi)
        if quota.deleted and undelete:
            # Undelete quota
            print("Restoring deleted quota")
            result = quota_client.undelete_quota(quota.id)
            print("%s" % result)
        # Do the update
        result = quota_client.update_quota(quota.id,
                                           name=name,
                                           description=description,
                                           amount=amount,
                                           operation=operation,
                                           default=default,
                                           in_users=users,
                                           in_groups=groups)
        if result:
            print("%s" % result)
        return 0
    except galaxy.client.ConnectionError as ex:
        logger.fatal("Failed to update quota:")
        logger.fatal(ex)
        return 1

def delete_quota(gi,name,no_confirm=False):
    """
    Delete the named quota from the Galaxy instance

    Arguments:
      gi: Galaxy instance
      name: name of the quota to delete
      no_confirm : if True then don't prompt to confirm the
        deletion operation
    """
    # Get the id for the quota
    quota = [q for q in get_quotas(gi) if q.name == name]
    if len(quota) != 1:
        logger.fatal("'%s': no such quota?" % name)
        return 1
    quota = quota[0]
    # Prompt user for confirmation
    if no_confirm or \
       prompt_for_confirmation("Delete quota '%s'?" % quota.name,
                               default="n"):
        # Delete the quota
        try:
            quota_client = galaxy.quotas.QuotaClient(gi)
            result = quota_client.delete_quota(quota.id)
            print("%s" % result)
            return 0
        except galaxy.client.ConnectionError as ex:
            logger.fatal("Failed to delete quota:")
            logger.fatal(ex)
            return 1
    else:
        print("Quota '%s' not deleted" % quota.name)
        return 0
