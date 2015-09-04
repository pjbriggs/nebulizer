#!/usr/bin/env python
#
# tools: functions for managing tools
import fnmatch
from bioblend import galaxy
from bioblend import toolshed
from bioblend.galaxy.client import ConnectionError

def list_tools(gi,name=None,installed_only=False):
    """
    """
    tool_client = galaxy.tools.ToolClient(gi)
    for tool in tool_client.get_tools():
        if name and not fnmatch.fnmatch(tool['name'].lower(),
                                        name.lower()):
            continue
        #print "%s" % tool
        # Tool info
        tool_name = tool['name']
        tool_id = tool['id']
        tool_version = tool['version']
        description = tool['description']
        panel_section = tool['panel_section_name']
        # Find the parent repository from tool id
        shed_client = galaxy.toolshed.ToolShedClient(gi)
        tool_repo = ''
        for repo in shed_client.get_repositories():
            repo_id = '/'.join((repo['tool_shed'],
                                'repos',
                                repo['owner'],
                                repo['name'],))
            repo_id = repo_id + '/'
            if tool_id.startswith(repo_id):
                tool_repo = '/'.join((repo['tool_shed'],
                                      repo['owner'],
                                      repo['name']),)
                break
        if installed_only and not tool_repo:
            continue
        # Print info
        print "%s\t%s\t%s" % (tool_name,
                              tool_version,
                              tool_repo)

def list_installed_repositories(gi,name=None,list_tools=False):
    """
    """
    shed_client = galaxy.toolshed.ToolShedClient(gi)
    for repo in shed_client.get_repositories():
        if repo['deleted']:
            continue
        if name and not fnmatch.fnmatch(repo['name'].lower(),
                                        name.lower()):
            continue
        #print "%s" % repo
        # Repository info
        repo_name = repo['name']
        repo_shed = repo['tool_shed']
        repo_owner = repo['owner']
        repo_revision_number = repo['ctx_rev']
        repo_changeset_revision = repo['changeset_revision']
        # Repository status
        status = repo['tool_shed_status']
        try:
            status_latest_revision = (status['latest_installable_revision']
                                      == 'True')
            status_revision_update = (status['revision_update'] == 'True')
            status_revision_upgrade = (status['revision_upgrade'] == 'True')
            status_deprecated = (status['repository_deprecated'] == 'True')
            status_indicator = ''
            if status_deprecated:
                status_indicator += 'D'
            elif status_latest_revision:
                status_indicator += '*'
            elif status_revision_update:
                status_indicator += 'u'
            elif status_revision_upgrade:
                status_indicator += 'U'
            else:
                status_indicator = ' '
        except (KeyError,TypeError):
            status_indicator = '?'
        # Print information
        print "%s %s\t%s\t%s\t%s:%s" % (status_indicator,
                                        repo_name,
                                        repo_shed,
                                        repo_owner,
                                        repo_revision_number,
                                        repo_changeset_revision)
        # Get tools associated with repo
        if list_tools:
            repo_id = '/'.join((repo_shed,'repos',repo_owner,repo_name,))
            repo_id = repo_id + '/'
            tool_client = galaxy.tools.ToolClient(gi)
            for tool in tool_client.get_tools():
                if tool['id'].startswith(repo_id):
                    print "- %s\t%s\t%s" % (tool['name'],
                                            tool['version'],
                                            tool['description'])

def list_tool_panel(gi):
    """
    """
    tool_client = galaxy.tools.ToolClient(gi)
    for item in tool_client.get_tool_panel():
        #print "%s" % item
        print "%s\t'%s'" % (item['id'],item['name'])

def install_tool(gi,tool_shed,name,owner,
                 revision=None,tool_panel_section=None):
    """
    """
    # Locate the repository on the toolshed
    shed = toolshed.ToolShedInstance(url=tool_shed)
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
    if tool_panel_section is not None:
        tool_panel_section_id = None
        tool_client = galaxy.tools.ToolClient(gi)
        for item in tool_client.get_tool_panel():
            if item['id'] == tool_panel_section or \
               item['name'] == tool_panel_section:
                tool_panel_section_id = item['id']
                print "Located existing tool panel section: %s" % \
                    tool_panel_section_id
                break
        if not tool_panel_section_id:
            print "New tool panel section: %s" % tool_panel_section
        else:
            tool_panel_section = None
    # Attempt to install
    print "Installing..."
    try:
        tool_shed_client = galaxy.toolshed.ToolShedClient(gi)
        tool_shed_client.install_repository_revision(
            tool_shed,name,owner,revision,
            install_tool_dependencies=True,
            install_repository_dependencies=True,
            tool_panel_section_id=tool_panel_section_id,
            new_tool_panel_section_label=tool_panel_section)
        print "Done"
        list_installed_repositories(gi,name,list_tools=True)
    except ConnectionError,ex:
        print "Error from Galaxy API: %s" % ex
        print "The tool may still be installing so please check"
