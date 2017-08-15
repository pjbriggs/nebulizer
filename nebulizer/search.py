#!/usr/bin/env python
#
# search: functions for searching toolshed
import logging
import string
from core import get_galaxy_instance
from tools import normalise_toolshed_url
from tools import get_repositories
from bioblend import toolshed
from bioblend import ConnectionError as BioblendConnectionError

# Logging
logger = logging.getLogger(__name__)

# Constants
SEARCH_PAGE_SIZE = 1000

# Functions

def search_toolshed(tool_shed,query_string,gi=None):
    """
    Search toolshed and print resulting matches

    Arguments:
      tool_shed (str): URL for tool shed to search
      query_string (str): text to use as query
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list tools which match this
        string (can include wildcards)
    """
    # Get a toolshed instance
    tool_shed_url = normalise_toolshed_url(tool_shed)
    shed = toolshed.ToolShedInstance(tool_shed_url)
    # Query the toolshed
    repo_client = toolshed.repositories.ToolShedRepositoryClient(shed)
    try:
        search_result = repo_client.search_repositories(
            query_string,
            page_size=SEARCH_PAGE_SIZE)
    except BioblendConnectionError as connection_error:
        # Handle error
        logger.warning("Error from Galaxy API: %s"
                       % connection_error)
        return connection_error.status_code
    # Deal with the results
    nhits = int(search_result['total_results'])
    if nhits == 0:
        print "No repositories found"
        return 0
    # Sort results on name
    hits = sorted(search_result['hits'],
                  key=lambda r: r['repository']['name'])
    # Get list of installed tool repositories
    if gi is not None:
        # Strip protocol from tool shed URL
        for proc in ('http://','https://'):
            if tool_shed_url.startswith(proc):
                tool_shed = tool_shed_url[len(proc):]
        # Restrict repos to this tool shed
        installed_repos = filter(lambda r:
                                 r.tool_shed == tool_shed,
                                 get_repositories(gi))
    else:
        installed_repos = []
    # Print the results
    for i,hit in enumerate(hits):
        # Get the repository details
        repo = hit['repository']
        name = repo['name']
        owner = repo['repo_owner_username']
        description = to_ascii(repo['description']).strip()
        # Look to see it's installed
        installed = bool(filter(lambda r:
                                r.name == name and
                                r.owner == owner,
                                installed_repos))
        if installed:
            status = "*"
        else:
            status = " "
        # Print details
        print "% 3d %s" % (i+1,
                           '\t'.join(["%s %s" % (status,name),
                                      owner,
                                      description]))
    print "%d repositor%s found" % (nhits,('y' if nhits == 1 else 'ies'))
    # Finished
    return 0

def to_ascii(s,replace_with='?'):
    """
    Convert a string to ASCII

    Converts the supplied string to ASCII by replacing
    any non-ASCII characters with the specified
    character (defaults to '?').
    """
    try:
        return str(s)
    except UnicodeEncodeError:
        s1 = []
        for c in s:
            if c in string.printable:
                s1.append(c)
            else:
                s1.append(replace_with)
        return ''.join(s1)
