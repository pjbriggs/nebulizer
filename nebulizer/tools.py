#!/usr/bin/env python
#
# tools: functions for managing tools
import fnmatch
import time
import json
import logging
from bioblend import galaxy
from bioblend import toolshed
from bioblend.galaxy.client import ConnectionError
from bioblend import ConnectionError as BioblendConnectionError
from .core import prompt_for_confirmation
from .core import Reporter

# Logging
logger = logging.getLogger(__name__)

# Constants
TOOL_INSTALL_OK = 0
TOOL_INSTALL_FAIL = 1
TOOL_INSTALL_TIMEOUT = 2
TOOL_INSTALL_PENDING = 3
TOOL_UPDATE_OK = 0
TOOL_UPDATE_FAIL = 1
TOOL_UNINSTALL_OK = 0
TOOL_UNINSTALL_FAIL = 1

# Classes

class Tool(object):
    """
    Class wrapping extraction of tool data

    Provides an interface for accessing data about a tool
    in a Galaxy instance, which has been retrieved via a
    call to the Galaxy API using bioblend.

    """
    def __init__(self,tool_data):
        """
        Create a new Tool instance

        ``tool_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for tool_data in galaxy.tools.ToolClient(gi).get_tools():
        >>>    print(Tool(tool_data).name)

        """
        self.name = tool_data['name']
        self.id = tool_data['id']
        self.version = tool_data['version']
        self.description = tool_data['description']
        self.panel_section = tool_data['panel_section_name']
        try:
            self.config_file = tool_data['config_file']
        except KeyError:
            self.config_file = None
        try:
            self.tool_shed_repository = tool_data['tool_shed_repository']
        except KeyError:
            self.tool_shed_repository = None

    @property
    def tool_repo(self):
        """
        Return the tool repository name

        The tool repository name is of the form

        TOOLSHED/OWNER/TOOL

        e.g. toolshed.g2.bx.psu.edu/devteam/tophat

        If the tool wasn't installed from a toolshed
        then an empty string is returned.

        """
        if self.tool_shed_repository:
            # Explicit repository information
            return '/'.join(
                [self.tool_shed_repository['tool_shed'],
                 self.tool_shed_repository['owner'],
                 self.tool_shed_repository['name']])
        # Older Galaxy: extract from the tool id
        ele = self.id.split('/')
        try:
            i = ele.index('repos')
            tool_shed = '/'.join(ele[:i])
            owner = ele[i+1]
            repo = ele[i+2]
            return '/'.join((tool_shed,owner,repo))
        except ValueError:
            return ''

    @property
    def tool_changeset(self):
        """
        Return the tool changeset revision

        This is a commit id of the form 'efc56ee1ade4'

        Returns None if a changeset revision can't be
        extracted

        """
        tool_repo = self.tool_repo
        if not tool_repo:
            return None
        if self.tool_shed_repository:
            # Explicit repository information
            return str(self.tool_shed_repository['changeset_revision'])
        # Older Galaxy: look for the config_file element - something
        # of the form:
        # .../toolshed.g2.bx.psu.edu/repos/devteam/picard/efc56ee1ade4/...
        try:
            ele = tool_repo.split('/')
            tool_shed = '/'.join(ele[:-2])
            owner = ele[-2]
            repo = ele[-1]
            search_string = "/repos/%s/%s/" % (owner,repo)
            i = self.config_file.index(search_string) + len(search_string)
            revision = self.config_file[i:].split('/')[0]
            return revision
        except (AttributeError,ValueError):
            return None

class RepositoryRevision(object):
    """
    Class wrapping extraction of toolshed repository version data

    Provides an interface for accessing data about the version
    data for a toolshed repository that has been installed into
    a Galaxy instance, and which has been retrieved via a call
    to the Galaxy API using bioblend.

    """
    def __init__(self,repo_data):
        """
        Create a new RepositoryRevision instance

        ``repo_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for repo_data in \
        >>>   galaxy.toolshed.ToolShedClient(gi).get_repositories():
        >>>   print(RepositoryRevision(repo_data).revision_number)

        However the RepositoryRevision class is most
        likely instantiated implicitly by an instance
        of the Repository class.

        """
        # Version numbers
        self.revision_number = repo_data['ctx_rev']
        self.changeset_revision = repo_data['changeset_revision']
        self.installed_changeset_revision = repo_data['installed_changeset_revision']
        self.status = repo_data['status']
        self.error_message = repo_data['error_message']
        self.deleted = repo_data['deleted']
        # Repository revision status
        revision = repo_data['tool_shed_status']
        try:
            self.latest_revision = (revision['latest_installable_revision']
                                    == 'True')
        except (KeyError,TypeError):
            self.latest_revision = None
        try:
            self.revision_update = (revision['revision_update'] == 'True')
        except (KeyError,TypeError):
            self.revision_update = None
        try:
            self.revision_upgrade = (revision['revision_upgrade'] == 'True')
        except (KeyError,TypeError):
            self.revision_upgrade = None
        try:
            self.deprecated = (revision['repository_deprecated'] == 'True')
        except (KeyError,TypeError):
            self.deprecated = None
        # Indicates whether a newer revision is installed
        self._newer_revision_installed = None
        # Indicates whether a newer revision is available on toolshed
        self._tool_shed_has_newer_revision = None

    def newer_revision_installed(self,status=None):
        """
        Query or set flag indicating if newer version is installed

        If ``status`` is set then should be True
        (indicating that a newer revision of the tool
        has been installed in the Galaxy instance) or
        False (no newer instance has been installed).

        Returns the last value of ``status`` that was
        explicitly specified, or 'None' if no status
        has been set.
        """
        if status is not None:
            self._newer_revision_installed = status
        return self._newer_revision_installed

    def tool_shed_has_newer_revision(self,status=None):
        """
        Query or set flag indicating if newer version is available on toolshed

        If ``status`` is set then should be True
        (indicating that a newer version of the tool
        is available on the toolshed) or False (no
        newer version is available).

        Returns the last value of ``status`` that was
        explicitly specified, or 'None' if no status
        has been set.
        """
        if status is not None:
            self._tool_shed_has_newer_revision = status
        return self._tool_shed_has_newer_revision

    @property
    def status_indicator(self):
        """
        Return 'status_indicator' string for the revision

        The status indicator is a concise way to
        summarise the status of the revision:

        'D' = deprecated
        '^' = newer revision installed
        'u' = update available but not installed
        'U' = upgrade available but not installed
        '!' = newer version available on toolshed
        '*' = this is latest revision

        """
        status_indicator = ''
        if self.deprecated:
            status_indicator += 'D'
        elif self.newer_revision_installed():
            status_indicator += '^'
        elif self.tool_shed_has_newer_revision():
            status_indicator += '!'
        elif self.latest_revision:
            status_indicator += '*'
        elif self.revision_update:
            status_indicator += 'u'
        elif self.revision_upgrade:
            status_indicator += 'U'
        else:
            status_indicator = ' '
        return status_indicator

    @property
    def revision_id(self):
        """
        Return revision id

        The revision id is a combination of the
        numerical revision number (1,2...) and the
        revision changeset hash. For example:

        2:a60283899c6d

        """
        return ':'.join((self.revision_number,
                         self.changeset_revision))

class Repository(object):
    """
    Class wrapping extraction of toolshed repository data

    Provides an interface for accessing data about a
    toolshed repository that has been installed into
    a Galaxy instance, and which has been retrieved via
    a call to the Galaxy API using bioblend.

    """
    def __init__(self,repo_data):
        """
        Create a new Repository instance

        ``repo_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for repo_data in \
        >>>   galaxy.toolshed.ToolShedClient(gi).get_repositories():
        >>>   print(Repository(repo_data).name)

        The Repository instance can store information
        on multiple revisions; additional revisions
        can be stored using the ``add_revision``
        method, and retrieved using the ``revisions``
        method.

        """
        self.name = repo_data['name']
        self.tool_shed = repo_data['tool_shed']
        self.owner = repo_data['owner']
        self._revisions = []
        self._tool_shed_revisions = None
        self.add_revision(repo_data)

    def add_revision(self,repo_data):
        """
        Add info on a specific revision

        ``repo_data`` is a dictionary returned by a
        call to bioblend.

        """
        self._revisions.append(RepositoryRevision(repo_data))
        # Sort into order (newest to oldest)
        self._revisions.sort(key=lambda r: int(r.revision_number),
                             reverse=True)
        # Find more recent installed version
        latest_installed_revision = None
        for i,r in enumerate(self._revisions):
            if not r.deleted:
                latest_installed_revision = \
                                self._revisions[i].changeset_revision
                break
        # Set status indicating whether newer version is
        # installed
        for r in self._revisions:
            r.newer_revision_installed(status=None)
        if latest_installed_revision is not None:
            self._revisions[i].newer_revision_installed(status=False)
            for r in self._revisions[i+1:]:
                r.newer_revision_installed(status=True)

    def update_tool_shed_revision_status(self):
        """
        Update the 'newer toolshed revision' status of the repository

        For each installed revision of the repository, set the
        ``tool_shed_has_newer_revision`` status to True if a
        newer revision is available on the toolshed, or False
        if not.
        """
        # Get the latest available revision from the toolshed
        tool_shed_revisions = self.tool_shed_revisions()
        if tool_shed_revisions is not None:
            latest_shed_revision = tool_shed_revisions[-1]
            if self._revisions[0].changeset_revision != latest_shed_revision:
                self._revisions[0].tool_shed_has_newer_revision(status=True)
            else:
                self._revisions[0].tool_shed_has_newer_revision(status=False)

    def tool_shed_revisions(self):
        """
        Fetch available repository revisions from toolshed

        Returns a list of the available installable revisions
        (aka changeset ids) from the toolshed, ordered oldest
        to newest.

        If the revision list can't be obtained (e.g. the tool
        shed is not available) then returns 'None', otherwise
        returns a list.
        """
        if self._tool_shed_revisions is None:
            # Fetch available revisions from the tool shed
            shed = toolshed.ToolShedInstance(url=self.tool_shed)
            try:
                self._tool_shed_revisions = \
                    shed.repositories.get_ordered_installable_revisions(
                        self.name,
                        self.owner)
            except BioblendConnectionError as connection_error:
                logger.critical("Unable to connect to toolshed '%s': %s" %
                                (self.tool_shed,connection_error.status_code))
        return self._tool_shed_revisions

    def revisions(self,include_deleted=False):
        """
        Return a list of installed revisions

        Arguments:
          include_deleted (bool): if True then include
            revisions marked as deleted (default is to
            omit deleted revisions)

        Returns:
          list: list of RepositoryRevision objects,
            in order of newest to oldest.

        """
        revisions = [x for x in self._revisions]
        if not include_deleted:
            revisions = [x for x in revisions if not x.deleted]
        return revisions

    @property
    def id(self):
        """
        Return an 'id' for the repo

        The id string is TOOL_SHED/OWNER/TOOL

        e.g. toolshed.g2.bx.psu.edu/devteam/tophat

        """
        return '/'.join((self.tool_shed,
                         self.owner,
                         self.name))

class ToolPanelSection(object):
    """
    Class wrapping extraction of tool panel sections

    Provides an interface for accessing data about a
    tool panel section in a Galaxy instance, and which
    has been retrieved via a call to the Galaxy API
    using bioblend.

    """
    def __init__(self,tool_panel_data):
        """
        Create a new ToolPanelSection instance

        ``tool_panel_data`` is a dictionary returned
        by a call to bioblend, for example:

        >>> galaxy.tools.ToolClient(gi)
        >>> for tool_data in galaxy.tools.ToolClient(gi).get_tools():
        >>>    print(ToolPanelSection(tool_data).name)

        """
        self.id = tool_panel_data['id']
        try:
            self.name = tool_panel_data['name']
        except KeyError:
            self.name = None
        self.model_class = tool_panel_data['model_class']
        self.elems = []
        try:
            for elem in tool_panel_data['elems']:
                self.elems.append(ToolPanelSection(elem))
        except KeyError:
            pass

    @property
    def is_toolsection(self):
        """
        Check if section is a tool panel section
        """
        return (self.model_class == "ToolSection")

    @property
    def is_tool(self):
        """
        Check if section is a tool
        """
        return (self.model_class == "Tool")

    @property
    def is_label(self):
        """
        Check if section is a tool panel label
        """
        return (self.model_class == "ToolSectionLabel")

class ToolPanel(object):
    """
    Class wrapping extraction of tool panel

    Provides an interface for accessing data about the
    tool panel in a Galaxy instance, and which
    has been retrieved via a call to the Galaxy API
    using bioblend.

    """
    def __init__(self,gi):
        """
        Create a new ToolPanel instance

        Arguments:
          gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
        """
        self.sections = []
        tool_client = galaxy.tools.ToolClient(gi)
        for data in tool_client.get_tool_panel():
            self.sections.append(ToolPanelSection(data))

    def tool_index(self,tool,strict=False):
        """
        Return index of tool in tool panel

        Given a tool, return an integer 'index'
        corresponding to the position of the tool in
        the tool panel.

        By default if a tool at the specified
        version is not located then the index of the
        closest matching tool which matches the toolshed,
        owner and repository name but not the version
        will be returned instead.

        This is intended to deal with multiple versions
        of the same tool, where only one version (normally
        the most recent) appears in the tool panel.
        Other versions of the tool are accessible in Galaxy
        by selecting them from within the tool, so they
        could be considered to be 'hidden behind' the
        version that is explicitly installed.

        This behaviour can be disabled by setting the
        'strict' argument to True.

        Arguments:
          tool (Tool): Tool instance
          strict (boolean): if True then only return
            an index if there is a precise match to the
            tool (default is to try and return closest
            match if precise match cannot be found)

        Returns:
          Integer: position of the tool in the tool
            panel, or -1 if it can't be located.
        """
        # Convenience variables
        tool_id = tool.id
        tool_id_no_version = '/'.join(tool_id.split('/')[:-1])
        index_ = -1
        fallback_index = None
        # Traverse tool panel looking for a match
        for section in self.sections:
            if section.is_toolsection:
                for elem in section.elems:
                    index_ += 1
                    if elem.id == tool_id:
                        return index_
                    elif elem.id.startswith(tool_id_no_version) and \
                         section.name == tool.panel_section:
                        fallback_index = index_
            elif section.is_tool:
                index_ += 1
                if section.id == tool_id:
                    return index_
                elif section.id.startswith(tool_id_no_version):
                    fallback_index = index_
        # Not found, return nearest index instead
        if not strict and fallback_index is not None:
            return fallback_index
        # Nothing matching at all
        return -1

# Functions

def get_tools(gi):
    """
    Return list of tools in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of Tool objects.

    """
    tools = []
    tool_client = galaxy.tools.ToolClient(gi)
    for tool_data in tool_client.get_tools():
        tools.append(Tool(tool_data))
    return tools

def get_repositories(gi):
    """
    Return list of repositories installed in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of Repository objects.

    """
    repos = []
    shed_client = galaxy.toolshed.ToolShedClient(gi)
    for repo_data in shed_client.get_repositories():
        repo = Repository(repo_data)
        existing_repos = [x for x in repos if x.id == repo.id]
        if not existing_repos:
            # No entry for this repository
            repos.append(repo)
        elif len(existing_repos) == 1:
            # Single match, add this as a revision
            existing_repos[0].add_revision(repo_data)
        else:
            # Multiple matches - error
            raise Exception("Multiple instances for %s?" %
                            repo.id)
    return repos

def get_tool_panel_sections(gi):
    """
    Return list of tool panel sections in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      list: list of ToolPanelSection objects.

    """
    tool_panel_sections = []
    tool_client = galaxy.tools.ToolClient(gi)
    for data in tool_client.get_tool_panel():
        tool_panel_sections.append(ToolPanelSection(data))
    return tool_panel_sections

def get_revisions_from_toolshed(tool_shed,name,owner):
    """
    Fetch list of installable revisions for a tool from its toolshed

    Arguments:
      tool_shed (str): tool shed URL
      name (str): name of the tool repository
      owner (str): tool repository owner

    Returns:
      List: ordered list (oldest to newest) of the
        installable repositoy changesets on the tool
        shed.
    """
    shed = toolshed.ToolShedInstance(url=tool_shed)
    try:
        return shed.repositories.get_ordered_installable_revisions(name,
                                                                   owner)
    except BioblendConnectionError as connection_error:
        logger.critical("Unable to connect to toolshed '%s': %s" %
                        (tool_shed,connection_error.status_code))
        return []

def handle_repository_spec(repo_spec):
    """
    Process an arbitrary repository specification

    Given a repository specification as list of one of
    more components, returns the toolshed URL, repository
    owner, repository name and revision.

    The specification can be any of the forms:

    - ('https://toolshed.g2.bx.psu.edu/view/devteam/fastqc/e7b2202befea',)
    - (https://toolshed.g2.bx.psu.edu/view/devteam/fastqc',)
    - ('devteam/fastqc/e7b2202befea',)
    - ('devteam/fastqc',)
    - ('toolshed.g2.bx.psu.edu','devteam','fastqc','e7b2202befea')
    - ('toolshed.g2.bx.psu.edu','devteam','fastqc')
    - ('devteam','fastqc')
    - ('devteam','fastqc','e7b2202befea')
    - ('devteam','fastqc','3:e7b2202befea')

    Revision is set to None if not found; toolshed is set
    to the main Galaxy toolshed if not found.

    The leading protocol (https://, http://) is removed
    from the toolshed URL.

    Returns the tuple of (TOOLSHED,OWNER,REPOSITORY,REVISION)
    """
    repository = list(repo_spec)
    repo0 = repository[0].strip('/')
    if not (repo0.startswith('https://') or repo0.startswith('http://')):
        # No protocol specified
        if repo0.split('/')[0].count('.') > 0:
            # First element contains dots so must be a URL
            # Assume toolshed URL with no leading protocol
            repo0 = 'https://' + repo0
            if len(repository) > 1:
                # More than one element so assume that
                # first element is URL without trailing
                # tool definition
                # Check it ends with 'view' or 'repo'
                if not repo0.split('/')[-1] in ('view','repo'):
                    # Append 'view' element
                    repo0 += '/view'
        else:
            # No toolshed: assume main Galaxy toolshed
            repo0 = "https://toolshed.g2.bx.psu.edu/view/" + repo0
    repository[0] = repo0
    tool_url = '/'.join(repository)
    # Decompose the URL into toolshed, owner, repository
    # and changeset components
    toolshed = list()
    owner = None
    repository = None
    revision = None
    for ix,ele in enumerate(tool_url.split('/')):
        if ele not in ('view','repo'):
            toolshed.append(ele)
        else:
            toolshed = '/'.join(toolshed)
            try:
                owner = tool_url.split('/')[ix+1]
                repository = tool_url.split('/')[ix+2]
            except IndexError:
                # Invalid specification
                raise Exception("Invalid repository "
                                "specification: '%s'" %
                                repo_spec)
            try:
                revision = tool_url.split('/')[ix+3]
            except IndexError:
                revision = None
            break
    # Strip off the protocol
    for protocol in ('http://','https://'):
        if toolshed.startswith(protocol):
            toolshed = toolshed[len(protocol):]
            break
    # Handle revision of the form "version:changeset"
    # e.g. 3:f19e18ab01b1
    if revision and ':' in revision:
        revision = revision.split(':')[1]
    return (toolshed,owner,repository,revision)

def normalise_toolshed_url(tool_shed):
    """
    Return complete URL for a tool shed

    Arguments:
      tool_shed (str): partial or full URL for a
        toolshed server

    Returns:
      str: full URL for toolshed, including
        leading protocol.

    """
    if tool_shed.startswith('http://') or \
       tool_shed.startswith('https://'):
        return tool_shed
    return "https://%s" % tool_shed

def tool_install_status(gi,tool_shed,owner,name,revision=None):
    """
    Return the installation status of a tool repo

    If a revision is not specified then will return the
    status of the most recent installed version (if there
    is one).

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      tool_shed (str): URL for the toolshed to install the
        tool from
      name (str): name of the tool repository
      owner (str): name of the tool repository owner
      revision (str): revision changeset specifying
        the tool repository version (optional)

    Returns:
      String: the tool repository installation status returned
        from Galaxy (or '?' if the status cannot be retrieved)

    """
    try:
        repos = get_repositories(gi)
    except ConnectionError as connection_error:
        logger.warning("Got connection error from Galaxy API: %s"
                       % connection_error.status_code)
        return "?"
    repos = [r for r in repos if (r.name == name and
                                  r.owner == owner and
                                  r.tool_shed == tool_shed)]
    if len(repos) != 1:
        logger.debug("Unable to fetch tool repository information")
        return "?"
    repo = repos[0]
    if revision:
        revisions = [v for v in repo.revisions()
                     if v.changeset_revision == revision]
    else:
        revisions = repo.revisions()
    if len(revisions) != 1:
        logger.debug("Unable to fetch tool repository revisions")
        return "?"
    rev = revisions[0]
    if rev.error_message:
        return rev.error_message
    return rev.status

def installed_repositories(gi,name=None,
                           tool_shed=None,
                           owner=None,
                           include_deleted=False,
                           only_updateable=False,
                           check_tool_shed=False):
    """
    Fetch a list of installed repository revisions

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list tool repositiories
        which match this string (can include wildcards)
      tool_shed (str): optional, only list tool
        repositories from toolsheds that match this string
        (can include wildcards)
      owner (str): optional, only list tool repositiories
        with owners who match this string (can include
        wildcards)
      list_tools (bool): if True then also list the tools
        provided by the repository
      include_deleted (bool): if True then also include
        repository revisions that are marked as deleted
        (default is to only show those which are not
        deleted)
      only_updateable (bool): if True then only report
        repositories that have uninstalled updates or
        upgrades available (default is to show all
        repositories and revisions)
      check_tool_shed (bool): if True then also check
        revisions against the tool shed, to determine if
        updates are available for each tool. NB this is
        an expensive operation to perform so is turned
        off by default

    Returns:
      List: a list of tuples consisting of three items
        (repository,revision,tools), where
        - 'repository' is a populated Repository instance
        - 'revision' is a populated RepositoryRevision
        - 'tools' is a list of Tool instances

    """
    # Get the list of installed repos
    installed_repos = []
    repos = get_repositories(gi)
    # Filter on name
    if name:
        name = name.lower()
        repos = [r for r in repos if fnmatch.fnmatch(r.name.lower(),name)]
    # Filter on toolshed
    if tool_shed:
        # Strip leading http(s)://
        for protocol in ('https://','http://'):
            if tool_shed.startswith(protocol):
                tool_shed = tool_shed[len(protocol):]
        repos = [r for r in repos if fnmatch.fnmatch(r.tool_shed,tool_shed)]
    # Filter on owner
    if owner:
        repos = [r for r in repos if fnmatch.fnmatch(r.owner,owner)]
    # Get list of tools
    tools = get_tools(gi)
    for repo in repos:
        # Also check against tool shed?
        if check_tool_shed:
            repo.update_tool_shed_revision_status()
        # Check each revision
        for revision in repo.revisions():
            # Exclude deleted revisions
            if not include_deleted and revision.deleted:
                continue
            # Exclude revisions that don't need updating
            if only_updateable and \
               (revision.newer_revision_installed() or
                (revision.latest_revision and
                 not revision.tool_shed_has_newer_revision())):
                continue
            # Fetch tools associated with this revision
            repo_tools = [t for t in tools
                          if (t.tool_repo == repo.id and
                              t.tool_changeset ==
                              revision.installed_changeset_revision)]
            # Append to the list
            installed_repos.append((repo,revision,repo_tools))
    # Finished
    return installed_repos

# Commands

def list_tools(gi,name=None,installed_only=False):
    """
    Print a list of the available tools

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list tools which match this
        string (can include wildcards)
      installed_only (bool): if True then only list those
        tools which are provided by toolshed repositories

    """
    tools = get_tools(gi)
    # Filter on name
    if name:
        name = name.lower()
        tools = [t for t in tools
                 if fnmatch.fnmatch(t.name.lower(),name)]
    # Filter on installed
    if installed_only:
        tools = [t for t in tools if t.tool_repo != '']
    # Sort into name order
    tools.sort(key=lambda x: x.name.lower())
    # Print info
    output = Reporter()
    for tool in tools:
        output.append((
            tool.name,tool.version,
            (tool.panel_section if tool.panel_section else ''),
            tool.tool_repo,
            (tool.tool_changeset if tool.tool_changeset else ''))
        )
    output.report()
    print("total %s" % len(tools))

def list_installed_repositories(gi,name=None,
                                tool_shed=None,
                                owner=None,
                                list_tools=False,
                                include_deleted=False,
                                only_updateable=False,
                                check_tool_shed=False,
                                tsv=False):
    """
    Print a list of the installed toolshed repositories

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list tool repositiories
        which match this string (can include wildcards)
      tool_shed (str): optional, only list tool
        repositories from toolsheds that match this string
        (can include wildcards)
      owner (str): optional, only list tool repositiories
        with owners who match this string (can include
        wildcards)
      list_tools (bool): if True then also list the tools
        provided by the repository
      include_deleted (bool): if True then also include
        repository revisions that are marked as deleted
        (default is to only show those which are not
        deleted)
      only_updateable (bool): if True then only report
        repositories that have uninstalled updates or
        upgrades available (default is to show all
        repositories and revisions)
      check_tool_shed (bool): if True then also check
        revisions against the tool shed, to determine if
        updates are available for each tool. NB this is
        an expensive operation to perform so is turned
        off by default
      tsv (bool): if True then output in a compact tab
        delimited format listing toolshed, owner,
        repository, changeset and tool panel section

    """
    # Get the list of installed repos
    repos = installed_repositories(gi,name=name,
                                   tool_shed=tool_shed,
                                   owner=owner,
                                   include_deleted=include_deleted,
                                   only_updateable=only_updateable,
                                   check_tool_shed=check_tool_shed)
    if tsv:
        # Output format for reinstallation of repositories
        tool_panel = ToolPanel(gi)
        # Sort into tool panel order
        repos = sorted(repos,
                       key=lambda r:
                       tool_panel.tool_index(r[2][0])
                       if r[2] else -1)
        # Filter out non-package, non-datamanager repositories
        # which can't be located in the tool panel
        repos = [r for r in repos if
                 (r[0].name.startswith("package_") or
                  r[0].name.startswith("data_manager_") or
                  (r[2] and tool_panel.tool_index(r[2][0]) > -1))]
        # Print details
        output = Reporter()
        for r in repos:
            repo,revision,tools = r
            if tools:
                tool_panel_section = tools[0].panel_section
            else:
                tool_panel_section = None
            output.append((repo.tool_shed,
                           repo.owner,
                           repo.name,
                           revision.changeset_revision,
                           (tool_panel_section
                            if tool_panel_section else '')))
        # Write out in TSV format
        output.report(delimiter='\t')
    else:
        # Denser more verbose format
        output = Reporter()
        nrevisions = 0
        for r in repos:
            # Print details
            repo,revision,tools = r
            output.append(('%s %s' % (revision.status_indicator,
                                      repo.name),
                           repo.tool_shed,
                           repo.owner,
                           revision.revision_id,
                           revision.status))
            nrevisions += 1
            # List tools associated with revision
            if list_tools:
                for tool in tools:
                    output.append(("-",
                                   tool.name,
                                   tool.version,
                                   tool.description))
        # Write to stdout
        output.report()
        print("total %s" % nrevisions)

def list_tool_panel(gi,name=None,list_tools=False):
    """
    Print a list of tool panel contents

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list sections which match
        this string (can include wildcards)
      list_tools (bool): if True then also print the
        tools under each tool panel section

    """
    # Get the list of tool panel sections
    tool_panel = ToolPanel(gi)
    # Filter on name
    if name:
        name = name.lower()
        sections = [s for s in tool_panel.sections
                    if fnmatch.fnmatch(s.name.lower(),name)]
    else:
        sections = tool_panel.sections
    # Get list of tools, if required
    if list_tools:
        tools = get_tools(gi)
    # Report
    output = Reporter()
    for section in sections:
        output.append(("'%s'" % section.name,
                       section.id))
        if list_tools:
            for tool in sorted([t for t in tools
                                if t.panel_section == section.name],
                               key=lambda t: tool_panel.tool_index(t)):
                output.append(("#%d" % tool_panel.tool_index(tool),
                               tool.name,
                               tool.version,
                               tool.description))
    output.report(rstrip=True)
    print("total %s" % len(sections))

def install_tool(gi,tool_shed,name,owner,revision=None,
                 tool_panel_section=None,
                 install_tool_dependencies=True,
                 install_repository_dependencies=True,
                 install_resolver_dependencies=True,
                 timeout=600,
                 poll_interval=10,no_wait=False):
    """
    Install a tool repository into a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      tool_shed (str): URL for the toolshed to install the
        tool from
      name (str): name of the tool repository
      owner (str): name of the tool repository owner
      revision (str): optional revision changeset specifying
        the tool version to install; if not supplied then
        the latest installable revision will be used.
        NB revision can include the revision number e.g.
        "5:f8b7dc21b4ee"; only the trailing changeset id
        will be used.
      tool_panel_section (str): optional, name or id of
        the tool panel section to install the tools under; if
        the tool panel section doesn't already exist it will
        be created.
      install_tool_dependencies (bool): optional, if True
        then install tool dependencies from the toolshed
        if possible (default).
      install_repository_dependencies (bool): optional, if
        True then install repository dependencies from the
        toolshed if possible (default).
      install_resolver_dependencies (bool): optional, if
        True then install dependencies using a resolver
        which supports this (e.g. conda) (default).
      timeout (int): optional, sets the maximum time (in
        seconds) to wait for a tool to complete installing
        before giving up (default is 600s). Ignored if
        'no_wait' is True.
      poll_interval (int): optional, sets the time interval
        for polling Galaxy to check if a tool has completed
        installing (default is to check every 10s). Ignored
        if 'no_wait' is True.
      no_wait (boolean): optional, if True then don't wait
        for tool installation to complete (default is False
        i.e. do wait for tool to finish installing).

    """
    # Locate the repository on the toolshed
    print("Toolshed  :\t%s" % tool_shed)
    print("Repository:\t%s" % name)
    print("Owner     :\t%s" % owner)
    if revision is not None:
        # Normalise revision if necessary
        if ':' in revision:
            revision = revision.split(':')[1]
        print("Revision  :\t%s" % revision)
    else:
        print("Revision  :\t<not specified>")
    # Information on dependency installation
    print("Install tool dependencies from toolshed      : "
          "%s" % ('yes' if install_tool_dependencies else 'no'))
    print("Install repository dependencies from toolshed: "
          "%s" % ('yes' if install_repository_dependencies else 'no'))
    print("Install dependencies using resolver          : "
          "%s" % ('yes' if install_resolver_dependencies else 'no'))
    # Check if tool is already installed
    install_status = tool_install_status(gi,tool_shed,owner,name,
                                         revision)
    if install_status.startswith("Installed"):
        print("%s: already installed (status is \"%s\")" % (name,
                                                            install_status))
        return TOOL_INSTALL_OK
    # Get available revisions
    revisions = get_revisions_from_toolshed(tool_shed,name,owner)
    if not revisions:
        logger.critical("%s: no installable revisions found" % name)
        return TOOL_INSTALL_FAIL
    # Revisions are listed oldest to newest
    if revision is not None:
        # Check that specified revision can be installed
        if revision not in revisions:
            logger.critical("%s: requested revision is not installable"
                             % name)
            return TOOL_INSTALL_FAIL
    else:
        # Set revision to the most recent
        revision = revisions[-1]
        print("Installing newest revision (%s)" % revision)
    # Check if tool is already installed
    install_status = tool_install_status(gi,tool_shed,owner,name,
                                         revision)
    if install_status.startswith("Installed"):
        print("%s: already installed (status is \"%s\")" % (name,
                                                            install_status))
        return TOOL_INSTALL_OK
    # Look up tool panel section
    tool_panel_section_id = None
    new_tool_panel_section = None
    if tool_panel_section is None:
        print("Installing into top level tool panel (no section specified)")
    else:
        # Look for an existing section which matches the
        # supplied name or id
        for section in get_tool_panel_sections(gi):
            if tool_panel_section == section.id or \
               tool_panel_section == section.name:
                # Found existing tool panel section
                tool_panel_section_id = section.id
                print("Installing into existing tool panel section: "
                      "'%s' (id '%s')" % (section.name,
                                          tool_panel_section_id))
                break
        if not tool_panel_section_id:
            # No matching section exists, make a new one
            print("Installing into new tool panel section: '%s'" %
                  tool_panel_section)
            new_tool_panel_section = tool_panel_section
    # Get toolshed URL
    tool_shed_url = normalise_toolshed_url(tool_shed)
    print("Toolshed URL: %s" % tool_shed_url)
    # Attempt to install
    print("%s: requesting installation" % name)
    try:
        tool_shed_client = galaxy.toolshed.ToolShedClient(gi)
        tool_shed_client.install_repository_revision(
            tool_shed_url,name,owner,revision,
            install_tool_dependencies=install_tool_dependencies,
            install_repository_dependencies=install_repository_dependencies,
            install_resolver_dependencies=install_resolver_dependencies,
            tool_panel_section_id=tool_panel_section_id,
            new_tool_panel_section_label=new_tool_panel_section)
    except ConnectionError as connection_error:
        # Handle API error
        logger.warning("Got error from Galaxy API on attempted install "
                       "(ignored)")
        logger.warning("Status code: %s" % connection_error.status_code)
        logger.warning("Message    : \"%s\"" %
                       json.loads(connection_error.body)["err_msg"])
    except Exception as ex:
        # Handle general error
        logger.warning("Error while requesting tool installation "
                       "(ignored)")
        logger.warning("Exception: %s" % ex)
    # Monitor installation status
    if not no_wait:
        print("Galaxy connection closed: monitoring installation")
    ntries = 0
    prev_status_msg = None
    while (ntries*poll_interval) < timeout:
        install_status = tool_install_status(gi,tool_shed,owner,
                                             name,revision)
        if install_status.startswith("Installed"):
            print("%s: installed (status is \"%s\")" % (name,
                                                        install_status))
            return TOOL_INSTALL_OK
        elif install_status.startswith("Installing") or \
             install_status == "New" or \
             install_status == "Cloning" or \
             install_status == "Never installed" or \
             install_status == "?":
            if no_wait:
                # Don't wait for install to complete
                print("%s: still installing (status is \"%s\")" %
                      (name,install_status))
                print("Not waiting for install to complete")
                return TOOL_INSTALL_PENDING
            # Monitor the tool installation status
            ntries += 1
            status_msg = "%s: installing (status is \"%s\")" % (name,
                                                                install_status)
            if status_msg != prev_status_msg:
                print(status_msg)
                prev_status_msg = status_msg
            time.sleep(poll_interval)
        else:
            logger.critical("%s: failed (%s)" % (name,install_status))
            return TOOL_INSTALL_FAIL
    # Reaching here means timed out
    logger.critical("%s: timed out waiting for install" % name)
    return TOOL_INSTALL_TIMEOUT

def update_tool(gi,tool_shed,name,owner,
                install_tool_dependencies=True,
                install_repository_dependencies=True,
                install_resolver_dependencies=True,
                timeout=600,poll_interval=10,
                no_wait=False,check_tool_shed=False):
    """
    Update a tool repository in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      tool_shed (str): URL for the toolshed to install the
        tool from
      name (str): name of the tool repository
      owner (str): name of the tool repository owner
      install_tool_dependencies (bool): optional, if True
        then install tool dependencies from the toolshed
        if possible (default).
      install_repository_dependencies (bool): optional, if
        True then install repository dependencies from the
        toolshed if possible (default).
      install_resolver_dependencies (bool): optional, if
        True then install dependencies using a resolver
        which supports this (e.g. conda) (default).
      timeout (int): optional, sets the maximum time (in
        seconds) to wait for a tool to complete installing
        before giving up (default is 600s). Ignored if
        'no_wait' is True.
      poll_interval (int): optional, sets the time interval
        for polling Galaxy to check if a tool has completed
        installing (default is to check every 10s). Ignored
        if 'no_wait' is True.
      no_wait (boolean): optional, if True then don't wait
        for tool installation to complete (default is False
        i.e. do wait for tool to finish installing).
      check_tool_shed (bool): if True then also check
        revisions against the tool shed, to determine if
        updates are available for the tool (default is
        False i.e. do not check status against toolshed)
    """
    # Locate the existing installation
    update_repo = None
    for repo in get_repositories(gi):
        if repo.tool_shed == tool_shed and \
           repo.name == name and \
           repo.owner == owner:
            update_repo = repo
            break
    if update_repo is None:
        logger.critical("%s: unable to find repository to update" %
                        name)
        return TOOL_UPDATE_FAIL
    # Check there is at least one installed revision
    installed_revisions = [r for r in update_repo.revisions()
                           if not r.deleted]
    if not installed_revisions:
        logger.fatal("%s: no revisions currently installed" % name)
        return TOOL_UPDATE_FAIL
    # Update the toolshed status
    if check_tool_shed:
        update_repo.update_tool_shed_revision_status()
    # Find latest installable revision
    if not update_repo.tool_shed_revisions():
        logger.critical("%s: no installable revisions found" % name)
        return TOOL_UPDATE_FAIL
    revision = update_repo.tool_shed_revisions()[-1]
    # Check that there is an update available
    for r in update_repo.revisions():
        if not r.deleted and (r.latest_revision and
                              not r.tool_shed_has_newer_revision()):
            print("%s: version %s already the latest version" %
                  (name,r.revision_id))
            return TOOL_UPDATE_OK
    # Locate tool panel section for existing tools
    tool_panel_section = None
    for tool in get_tools(gi):
        if tool.tool_repo == update_repo.id:
            tool_panel_section = tool.panel_section
            break
    if tool_panel_section is None:
        logger.warning("%s: no tool panel section found" % name)
    #print("Installing update under %s" % tool_panel_section)
    return install_tool(
        gi,tool_shed,name,owner,revision,
        install_tool_dependencies=install_tool_dependencies,
        install_repository_dependencies=install_repository_dependencies,
        install_resolver_dependencies=install_resolver_dependencies,
        tool_panel_section=tool_panel_section,
        timeout=timeout,poll_interval=poll_interval,
        no_wait=no_wait)

def uninstall_tool(gi,tool_shed,name,owner,revision,
                   remove_from_disk=False,no_confirm=False):
    """
    Uninstall a tool repository from a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      tool_shed (str): URL for the toolshed to install the
        tool from
      name (str): name of the tool repository
      owner (str): name of the tool repository owner
      revision (str): revision changeset to uninstall;
        if set to '*' then matches all installed
        revisions.
      remove_from_disk (bool): optional, if True then also
        remove the repository from disk (otherwise it is
        only deactivated).
      no_confirm : if True then don't prompt to confirm the
        uninstall operation.

    """
    # Locate existing tool to remove
    uninstall_repos = [r for r in get_repositories(gi)
                       if r.tool_shed == tool_shed
                       and r.name == name
                       and r.owner == owner]
    if not uninstall_repos:
        logger.fatal("%s/%s: no matching tool installed?" % (owner,name))
        return TOOL_UNINSTALL_FAIL
    elif len(uninstall_repos) > 1:
        logger.fatal("%s/%s: matches multiple installed tools?" %
                     (owner,name))
        return TOOL_UNINSTALL_FAIL
    else:
        uninstall_repo = uninstall_repos[0]
    # Identify revisions
    if revision is not None:
        remove_revisions = [r for r in uninstall_repo.revisions()
                            if revision == '*'
                            or revision == r.changeset_revision]
    else:
        remove_revisions = uninstall_repo.revisions()
        if len(remove_revisions) > 1:
            logger.fatal("%s/%s: no revision specified but multiple "
                         "revisions are installed" % (owner,name))
            return TOOL_UNINSTALL_FAIL
    if not remove_revisions:
        logger.fatal("%s/%s%s: no matching installed revision?" %
                     (owner,name,
                      '/%s' % revision if revision is not None else ''))
        return TOOL_UNINSTALL_FAIL
    # Get toolshed URL
    tool_shed_url = normalise_toolshed_url(tool_shed)
    print("Toolshed URL: %s" % tool_shed_url)
    # Report and confirm uninstall
    print("\nThe following tools will be uninstalled:\n")
    for r in remove_revisions:
        print("\t%s %s/%s %s" % (tool_shed,owner,name,r.revision_id))
    print("")
    if (not no_confirm) and \
       (not prompt_for_confirmation("Proceed?",default="n")):
        print("Uninstall cancelled")
        return TOOL_UNINSTALL_OK
    # Attempt to uninstall each revision
    uninstall_status = TOOL_UNINSTALL_OK
    for revision in remove_revisions:
        try:
            print("%s/%s: requesting uninstall" % (name,
                                                   revision.revision_id))
            tool_shed_client = galaxy.toolshed.ToolShedClient(gi)
            result = tool_shed_client.uninstall_repository_revision(
                name,owner,revision.changeset_revision,
                tool_shed_url,remove_from_disk=remove_from_disk)
            print("* %s" % result['message'])
        except ConnectionError as connection_error:
            # Handle API error
            logger.warning("Got error from Galaxy API on attempted uninstall "
                           "(ignored)")
            logger.warning(connection_error)
            logger.warning("Status code: %s" % connection_error.status_code)
            logger.warning("Message    : \"%s\"" %
                           json.loads(connection_error.body)["err_msg"])
        except Exception as ex:
            # Handle general error
            logger.warning("Error while requesting tool uninstall "
                           "(ignored)")
            logger.warning("Exception: %s" % ex)
            uninstall_status = TOOL_UNINSTALL_FAIL
    return uninstall_status
