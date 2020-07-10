#!/usr/bin/env python
#
# search: functions for searching toolshed
import logging
import string
from fnmatch import fnmatch
from .core import get_galaxy_instance
from .core import Reporter
from .tools import normalise_toolshed_url
from .tools import get_repositories
from bioblend import toolshed
from bioblend import ConnectionError as BioblendConnectionError

# Logging
logger = logging.getLogger(__name__)

# Constants
SEARCH_PAGE_SIZE = 1000

# Functions

def search_toolshed(tool_shed,query_string,gi=None,
                    long_listing_format=False):
    """
    Search toolshed and print resulting matches

    Arguments:
      tool_shed (str): URL for tool shed to search
      query_string (str): text to use as query
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      long_listing_format (boolean): if True then use a
        long listing format when reporting items
    """
    # Get a toolshed instance
    tool_shed_url = normalise_toolshed_url(tool_shed)
    shed = toolshed.ToolShedInstance(tool_shed_url)
    print("Searching %s" % tool_shed_url)
    # Remove wildcards from start and end of query string
    shed_query_string = query_string.strip("*")
    # Query the toolshed
    repo_client = toolshed.repositories.ToolShedRepositoryClient(shed)
    try:
        search_result = repo_client.search_repositories(
            shed_query_string,
            page_size=SEARCH_PAGE_SIZE)
    except BioblendConnectionError as connection_error:
        # Handle error
        logger.warning("Error from Galaxy API: %s"
                       % connection_error)
        return connection_error.status_code
    # Filter on name
    hits = [r for r in search_result['hits'] if
            fnmatch(r["repository"]["name"].lower(),query_string)]
    # Deal with the results
    nhits = len(hits)
    if nhits == 0:
        print("No matching repositories found")
        return 0
    # Get additional details for each repo
    repositories = list()
    for hit in hits:
        # Get the repository details
        repo = hit['repository']
        name = repo['name']
        owner = repo['repo_owner_username']
        description = to_ascii(repo['description']).strip()
        # Get installable revisions
        installable_revisions = list()
        for revision in \
                repo_client.get_ordered_installable_revisions(name,owner):
            # Get details for each revision
            revision_info = \
                repo_client.get_repository_revision_install_info(
                    name,
                    owner,
                    revision)
            # Returns a 3 element list, only want details
            # from the last one
            # See https://bioblend.readthedocs.io/en/latest/api_docs/toolshed/all.html#bioblend.toolshed.repositories.ToolShedRepositoryClient.get_repository_revision_install_info
            revision_info = revision_info[2]
            version = revision_info[name][3]
            installable_revisions.append(dict(revision=revision,
                                              version=version,
                                              info=revision_info))
        # Sort the installable revisions on version number
        installable_revisions = sorted(installable_revisions,
                                       key=lambda r: int(r['version']),
                                       reverse=True)
        # Sort repo details
        repositories.append(dict(name=name,
                                 owner=owner,
                                 description=description,
                                 revisions=installable_revisions))
    # Get list of installed tool repositories
    if gi is not None:
        # Strip protocol from tool shed URL
        tool_shed = tool_shed_url
        for proc in ('http://','https://'):
            if tool_shed.startswith(proc):
                tool_shed = tool_shed[len(proc):]
        # Strip trailing slash
        tool_shed = tool_shed.rstrip('/')
        # Restrict repos to this tool shed
        installed_repos = [r for r in get_repositories(gi)
                           if r.tool_shed == tool_shed]
    else:
        installed_repos = []
    # Print the results
    print("")
    output = Reporter()
    for repository in repositories:
        # Get the repository details
        name = repository['name']
        owner = repository['owner']
        description = repository['description']
        # Iterate over revisions
        for revision in repository['revisions']:
            changeset = revision['revision']
            version = revision['version']
            # Look to see it's installed
            installed = bool([r for r in installed_repos
                              if (r.name == name and
                                  r.owner == owner and
                                  changeset in [rv.changeset_revision
                                                for rv in r.revisions()])])
            if installed:
                status = "*"
            else:
                status = " "
            # Print details
            if not long_listing_format:
                display_items = [owner,name,
                                 "%s:%s" % (version,changeset),
                                 status]
                output.append(display_items)
            else:
                output.append(("Name",name))
                output.append(("Owner",owner))
                output.append(("Revision","%s:%s" % (version,changeset)))
                output.append(("Description",description))
                if gi is not None:
                    if installed:
                        output.append(("Installed","yes"))
                    else:
                        output.append(("Installed","no"))
                output.append(("",))
    if not long_listing_format:
        output.report(prefix=" ")
    else:
        output.report(delimiter=": ")
    print("\n%d repositor%s found" % (nhits,('y' if nhits == 1 else 'ies')))
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
