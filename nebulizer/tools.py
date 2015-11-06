#!/usr/bin/env python
#
# tools: functions for managing tools
import fnmatch
from bioblend import galaxy
from bioblend import toolshed
from bioblend.galaxy.client import ConnectionError

# Classes

class Tool:
    """
    Class wrapping extraction of tool data

    Provides an interface for accessing data about a tool
    in a Galaxy instance, which has been retrieved via a
    a call to the Galaxy API using bioblend.

    """
    def __init__(self,tool_data):
        """
        Create a new Tool instance

        ``tool_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for tool_data in galaxy.tools.ToolClient(gi).get_tools():
        >>>    print Tool(tool_data).name

        """
        self.name = tool_data['name']
        self.id = tool_data['id']
        self.version = tool_data['version']
        self.description = tool_data['description']
        self.panel_section = tool_data['panel_section_name']

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
        ele = self.id.split('/')
        try:
            i = ele.index('repos')
            toolshed = '/'.join(ele[:i])
            owner = ele[i+1]
            repo = ele[i+2]
            return '/'.join((toolshed,owner,repo))
        except ValueError:
            return ''

class RepositoryRevision:
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
        >>>   print RepositoryRevision(repo_data).revision_number

        However the RepositoryRevision class is most
        likely instantiated implicitly by an instance
        of the Repository class.

        """
        # Version numbers
        self.revision_number = repo_data['ctx_rev']
        self.changeset_revision = repo_data['changeset_revision']
        self.status = repo_data['status']
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

    def newer_revision_installed(self,status=None):
        """
        Query or set flag indicating if newer version is installed

        If ``status`` is set then should be True
        (indicating that a newer revision of the tool
        has been installed in the Galaxy instance) or
        False (no newer instance has been installed).

        Returns the last value of ``status`` that was
        explicitly specified.

        """
        if status is not None:
            self._newer_revision_installed = status
        return self._newer_revision_installed

    @property
    def status_indicator(self):
        """
        Return 'status_indicator' string for the revision

        The status indicator is a concise way to
        summarise the status of the revision:

        'D' = deprecated
        '^' = newer revision installed
        'u' = update available but not installed
        'U' = ugrade available but not installed
        '*' = this is latest revision

        """
        status_indicator = ''
        if self.deprecated:
            status_indicator += 'D'
        elif self.newer_revision_installed():
            status_indicator += '^'
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

class Repository:
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
        >>>   print Repository(repo_data).name

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
        # Set status indicating whether newer version is
        # installed
        for r in self._revisions:
            r.newer_revision_installed(status=None)
        latest_revision = None
        for i,r in enumerate(self._revisions):
            if not r.deleted:
                latest_revision = i
                break
        if latest_revision is not None:
            self._revisions[i].newer_revision_installed(status=False)
            for r in self._revisions[i+1:]:
                r.newer_revision_installed(status=True)

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
            revisions = filter(lambda x: not x.deleted,revisions)
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

class ToolPanelSection:
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
        >>>    print ToolPanelSection(tool_data).name

        """
        self.id = tool_panel_data['id']
        self.name = tool_panel_data['name']

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
        existing_repos = filter(lambda x: x.id == repo.id,repos)
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

def normalise_toolshed_url(toolshed):
    """
    Return complete URL for a tool shed

    Arguments:
      toolshed (str): partial or full URL for a
        toolshed server

    Returns:
      str: full URL for toolshed, including
        leading protocol.

    """
    if toolshed.startswith('http://') or \
       toolshed.startswith('https://'):
        return toolshed
    return "https://%s" % toolshed

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
        tools = filter(lambda t: fnmatch.fnmatch(t.name.lower(),name),
                       tools)
    # Filter on installed
    if installed_only:
        tools = filter(lambda t: t.tool_repo != '',tools)
    # Sort into name order
    tools.sort(key=lambda x: x.name.lower())
    # Print info
    for tool in tools:
        print "%-16s\t%-8s\t%-16s\t%s" % (tool.name,
                                          tool.version,
                                          tool.panel_section,
                                          tool.tool_repo)
    print "total %s" % len(tools)

def list_installed_repositories(gi,name=None,list_tools=False,
                                include_deleted=False,
                                only_updateable=False):
    """
    Print a list of the installed toolshed repositories

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      name (str): optional, only list tool repositiories
        which match this string (can include wildcards)
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

    """
    # Get the list of installed repos
    repos = get_repositories(gi)
    # Filter on name
    if name:
        name = name.lower()
        repos = filter(lambda r: fnmatch.fnmatch(r.name.lower(),name),
                       repos)
    # Get list of tools, if required
    if list_tools:
        tools = get_tools(gi)
    # Report
    nrevisions = 0
    for repo in repos:
        # Check each revision
        for revision in repo.revisions():
            # Exclude deleted revisions
            if not include_deleted and revision.deleted:
                continue
            # Exclude revisions that don't need updating
            if only_updateable and \
               (revision.newer_revision_installed() or \
                revision.latest_revision):
                continue
            # Print details
            print "%s" % '\t'.join(('%s %s' % (revision.status_indicator,
                                               repo.name),
                                    repo.tool_shed,
                                    repo.owner,
                                    revision.revision_id,
                                    revision.status))
            nrevisions += 1
            # Get tools associated with repo
            if list_tools:
                for tool in filter(lambda t: t.tool_repo == repo.id,tools):
                    print "- %s" % '\t'.join((tool.name,
                                              tool.version,
                                              tool.description))
    print "total %s" % nrevisions

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
    sections = get_tool_panel_sections(gi)
    # Filter on name
    if name:
        name = name.lower()
        sections = filter(lambda s: fnmatch.fnmatch(s.name.lower(),name),
                          sections)
    # Get list of tools, if required
    if list_tools:
        tools = get_tools(gi)
    # Report
    for section in sections:
        print "'%s' (%s)" % (section.name,
                             section.id)
        if list_tools:
            for tool in filter(lambda t: t.panel_section == section.name,
                               tools):
                print "- %s" % '\t'.join((tool.name,
                                          tool.version,
                                          tool.description))
    print "total %s" % len(sections)

def install_tool(gi,tool_shed,name,owner,
                 revision=None,tool_panel_section=None):
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
        the latest installable revision will be used
      tool_panel_section (str): optional, name or id of
        the tool panel section to install the tools under; if
        the tool panel section doesn't already exist it will
        be created.

    """
    # Locate the repository on the toolshed
    shed = toolshed.ToolShedInstance(url=tool_shed)
    print "Toolshed:\t%s" % tool_shed
    print "Repository:\t%s" % name
    print "Owner:\t%s" % owner
    revisions = shed.repositories.get_ordered_installable_revisions(name,
                                                                    owner)
    #print "%s" % revisions
    if not revisions:
        print "No installable revisions found"
        return
    # Revisions are listed oldest to newest
    if revision is not None:
        # Check that specified revision can be installed
        if revision not in revisions:
            print "Requested revision is not installable"
            return
    else:
        # Set revision to the most recent
        revision = revisions[-1]
        print "Installing newest revision (%s)" % revision
    # Look up tool panel
    tool_panel_section_id = None
    if tool_panel_section is not None:
        for section in get_tool_panel_sections(gi):
            if tool_panel_section == section.id or \
               tool_panel_section == section.name:
                tool_panel_section_id = section.id
                print "Located existing tool panel section: '%s'" % \
                    tool_panel_section_id
                break
        if not tool_panel_section_id:
            print "New tool panel section: '%s'" % tool_panel_section
        else:
            tool_panel_section = None
    # Get toolshed URL
    tool_shed_url = normalise_toolshed_url(tool_shed)
    print "Toolshed URL: %s" % tool_shed_url
    # Attempt to install
    print "Installing..."
    try:
        tool_shed_client = galaxy.toolshed.ToolShedClient(gi)
        tool_shed_client.install_repository_revision(
            tool_shed_url,name,owner,revision,
            install_tool_dependencies=True,
            install_repository_dependencies=True,
            tool_panel_section_id=tool_panel_section_id,
            new_tool_panel_section_label=tool_panel_section)
        print "Done"
        list_installed_repositories(gi,name,list_tools=True)
    except ConnectionError,ex:
        print "Error from Galaxy API: %s" % ex
        print "The tool may still be installing so please check"

def update_tool(gi,tool_shed,name,owner):
    """
    Update a tool repository in a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance
      tool_shed (str): URL for the toolshed to install the
        tool from
      name (str): name of the tool repository
      owner (str): name of the tool repository owner

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
        print "Unable to find repository for update"
        return
    print "Toolshed:\t%s" % tool_shed
    print "Repository:\t%s" % name
    print "Owner:\t%s" % owner
    # Check that there is an update available
    for r in repo.revisions():
        if not r.deleted and r.latest_revision:
            print "Version %s already the latest version" \
                % r.revision_id
            return
    # Find latest installable revision
    shed = toolshed.ToolShedInstance(url=tool_shed)
    revisions = shed.repositories.get_ordered_installable_revisions(name,
                                                                    owner)
    if not revisions:
        print "No installable revisions found"
        return
    revision = revisions[-1]
    # Locate tool panel section for existing tools
    tool_panel_section = None
    for tool in get_tools(gi):
        if tool.tool_repo == update_repo.id:
            tool_panel_section = tool.panel_section
            break
    if tool_panel_section is None:
        print "No tool panel section found"
        return
    #print "Installing update under %s" % tool_panel_section
    install_tool(gi,tool_shed,name,owner,
                 tool_panel_section=tool_panel_section)
