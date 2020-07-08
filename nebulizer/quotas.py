#!/usr/bin/env python
#
# quotas: functions for managing quotas
import logging
import fnmatch
from bioblend import galaxy
from bioblend import ConnectionError
from .users import User
from .groups import Group

# Logging
logger = logging.getLogger(__name__)

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

def get_quotas(gi):
    """
    Return list of quotas from a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of Quota objects.

    """
    quotas = []
    quota_client = galaxy.quotas.QuotaClient(gi)
    for quota_data in quota_client.get_quotas():
        quota = Quota(quota_data)
        quota.update(quota_client.show_quota(quota.id))
        quotas.append(quota)
    return quotas

def list_quotas(gi,name=None,long_listing_format=False):
    """
    List quotas in Galaxy instance

    Arguments:
      gi    : Galaxy instance
      name  : optionally, only list matching quota names
      long_listing_format (boolean): if True then use a
        long listing format when reporting items

    """
    # Get quota data
    try:
        quotas = get_quotas(gi)
    except ConnectionError as ex:
        logger.fatal("Failed to get quota list: %s (%s)" % (ex.body,
                                                            ex.status_code))
        return 1
    # Filter quota list on supplied name
    if name:
        name = name.lower()
        quotas = [q for q in quotas
                  if fnmatch.fnmatch(q.name.lower(),name)]
    # Report quotas
    quotas.sort(key=lambda q: q.name.lower())
    for quota in quotas:
        n_users = len(quota.list_users)
        n_groups = len(quota.list_groups)
        if not long_listing_format:
            # Collect data items to report on a single line
            display_items = [quota.name,
                             "%s%s" % (quota.operation,
                                       quota.display_amount),
                             "%s" % quota.default_for
                             if quota.default_for else '',
                             "%s user%s" %
                             (n_users,'' if n_users == 1 else 's'),
                             "%s group%s" %
                             (n_groups,'' if n_groups == 1 else 's')]
            print('\t'.join([str(x) for x in display_items]))
        else:
            # Long listing format reports each quota in
            # a block
            print("Quota name : %s" % quota.name)
            print("Description: %s" % quota.description)
            print("Operation  : %s" % quota.operation)
            print("Amount     : %s" % quota.display_amount)
            print("Default    : %s" % quota.default_for)
            print("%s user%s" % (n_users,'' if n_users == 1 else 's'))
            for user in quota.list_users:
                print("\t%s" % user.email)
            print("%s group%s" % (n_groups,'' if n_groups == 1 else 's'))
            for group in quota.list_groups:
                print("\t%s" % group.name)
            print("")
    print("total %s" % len(quotas))
