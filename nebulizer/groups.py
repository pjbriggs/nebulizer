#!/usr/bin/env python
#
# groups: functions for managing groups
import logging
from bioblend import galaxy

# Logging
logger = logging.getLogger(__name__)

class Group(object):
    """
    Class wrapping extraction of group data

    Provides an interface for accessing data about a group
    in a Galaxy instance, which has been retrieved via a
    a call to the Galaxy API using bioblend.

    """
    def __init__(self,group_data):
        """
        Create a new Group instance

        ``group_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for group_data in galaxy.groups.GroupClient(gi).get_groups():
        >>>    print(Group(group_data).name)

        """
        # Initialise
        self.id = group_data['id']
        self.name = group_data['name']
        # Populate with additional data items
        self.update(group_data)

    def update(self,group_data):
        """
        Update the data items associated with the group

        ``group_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> group.update(galaxy.groups.GroupClient(gi).show_group(group.id))

        """
        # Check this is the same user ID
        if group_data['id'] != self.id:
            raise Exception("Tried to update data for user ID '%s' "
                            "with data for user ID '%s'" %
                            (self.id,
                             group_data['id']))
        # Update the attributes
        for attr in group_data.keys():
            try:
                setattr(self,attr,group_data[attr])
            except AttributeError:
                pass

# Functions

def get_groups(gi):
    """
    Return list of groups in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of Group objects.

    """
    groups = []
    group_client = galaxy.groups.GroupsClient(gi)
    # Get (undeleted) groups
    for group_data in group_client.get_groups():
        group = Group(group_data)
        group.update(group_client.show_group(group.id))
        groups.append(group)
    return groups
