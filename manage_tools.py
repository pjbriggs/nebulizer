#!/usr/bin/env python
#
# Manage tools in a Galaxy instance
import sys
import optparse
import nebulizer

"""
manage_tools.py

"""

__version__ = '0.0.1'

if __name__ == "__main__":
    # Initialise parser with common options
    p = optparse.OptionParser(usage=\
                              "\n\t%prog [options] CMD GALAXY_URL [args...]",
                              version="%%prog %s" % __version__,
                              description="Manage tools in the specified "
                              "Galaxy instance.")
    p.add_option('-k','--api_key',action='store',dest='api_key',default=None,
                 help="specify API key for GALAXY_URL (otherwise will try to "
                 "look up from .nebulizer file)")
    p.add_option('-n','--no-verify',action='store_true',dest='no_verify',default=False,
                 help="don't verify HTTPS connections")
    # Get major command and Galaxy URL or alias
    if len(sys.argv) < 3:
        p.error("Need to supply a command and Galaxy URL or alias")
    command = sys.argv[1]
    galaxy_url = sys.argv[2]

    # Populate parser with additional arguments depending on
    # major command
    if command == 'list':
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific tool name(s) to list")
    elif command == 'installed':
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific tool repository/ies to list")
        p.add_option('--list-tools',action='store_true',dest='list_tools',
                     default=None,
                     help="list the associated tools for each repository")
    elif command == 'install':
        p.add_option('--tool-panel-section',action='store',
                     dest='tool_panel_section',default=None,
                     help="tool panel section name or id to install the "
                     "tool under")

    # Process remaining arguments on command line
    options,args = p.parse_args(sys.argv[3:])
    api_key = options.api_key
    verify = not options.no_verify
    if not verify:
        sys.stderr.write("WARNING SSL certificate verification has been disabled\n")
        nebulizer.turn_off_urllib3_warnings()

    

    # Set up Nebulizer instance to interact with Galaxy
    ni = nebulizer.Nebulizer(galaxy_url,api_key,verify=verify)

    # Handle commands
    if command == 'list':
        ni.list_tools(name=options.name)
    elif command == 'installed':
        ni.list_installed_repositories(name=options.name,
                                       list_tools=options.list_tools)
    elif command == 'tool_panel':
        ni.list_tool_panel()
    elif command == 'install':
        if len(args) < 3:
            p.error("Usage: install TOOLSHED OWNER REPO [REV]")
        toolshed,owner,repo = args[:3]
        if len(args) == 4:
            revision = args[3]
        else:
            revision = None
        ni.install_tool(toolshed,repo,owner,
                        revision=revision,
                        tool_panel_section=options.tool_panel_section)

