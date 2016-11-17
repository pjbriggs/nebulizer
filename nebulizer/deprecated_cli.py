#!/usr/bin/env python
#
# deprecated_cli: deprecated CLI commands
import sys
import os
import optparse
import logging
from nebulizer import get_version
from .core import get_galaxy_instance
from .cli import handle_ssl_warnings
from .cli import handle_debug
from .cli import handle_suppress_warnings
from .cli import handle_credentials
import users
import libraries
import tools

logger = logging.getLogger(__name__)

def deprecation_warning():
    """
    Issue a deprecation warning
    """
    logger.warning("*********** THIS UTILITY IS NOW DEPRECATED ***********")
    logger.warning("*********** Use 'nebulizer CMD...' instead ***********")

def base_parser(usage=None,description=None):
    """
    Create base parser with common options

    """
    p = optparse.OptionParser(usage=usage,
                              version="%s" % get_version(),
                              description=description)
    p.add_option('-k','--api_key',action='store',dest='api_key',
                 default=None,
                 help="specify API key to use for connecting to "
                 "Galaxy instance. Must be supplied if there is "
                 "no API key stored for the specified instance, "
                 "(unless --username option is specified). If "
                 "there is a stored API key this overrides it.")
    p.add_option('-u','--username',action='store',dest='username',
                 default=None,
                 help="specify username (i.e. email) for connecting "
                 "to Galaxy instance, as an alternative to using "
                 "the API key. Prompts for a password unless one "
                 "is supplied via the --galaxy_password option.")
    p.add_option('-P','--galaxy_password',action='store',
                 dest='galaxy_password',default=None,
                 help="supply password for connecting to Galaxy "
                 "instance, when using the --username option.")
    p.add_option('-n','--no-verify',action='store_true',dest='no_verify',
                 default=False,help="don't verify HTTPS "
                 "connections. Use this when connecting to a Galaxy "
                 "instance which uses self-signed certificates.")
    p.add_option('-q','--suppress-warnings',action='store_true',
                 dest='suppress_warnings',
                 default=False,help="suppress warning messages "
                 "from nebulizer")
    p.add_option('--debug',action='store_true',dest='debug',
                 default=False,help="turn on debugging output")
    return p
    
def manage_users(args=None):
    """
    Implements the 'manage_users' utility

    """
    deprecation_warning()
    if args is None:
        args = sys.argv[1:]

    p = base_parser(usage=\
                    "\n\t%prog list   GALAXY_URL [options]"
                    "\n\t%prog create GALAXY_URL EMAIL [PUBLIC_NAME]"
                    "\n\t%prog create GALAXY_URL -t TEMPLATE START [END]"
                    "\n\t%prog create GALAXY_URL -b FILE [options]",
                    description="Manage and create users in a Galaxy "
                    "instance")
    commands = ['list','create']

    # Get compulsory arguments
    if len(args) == 1:
        if args[0] == '-h' or args[0] == '--help':
            p.print_usage()
        elif args[0] == '--version':
            p.print_version()
        sys.exit(0)
    if len(args) < 2:
        p.error("need to supply a command and a Galaxy URL/alias")
    command = args[0]
    galaxy_url = args[1]

    # Setup additional command line options
    if command not in commands:
        p.error("unrecognised command: '%s'" % command)
    elif command == 'list':
        p.set_usage("%prog list GALAXY_URL [options]")
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific emails/user name(s) to list")
        p.add_option('-l',action='store_true',
                     dest='long_listing_format',default=False,
                     help="use a long listing format (include ids, "
                     "disk usage and admin status)")
    elif command == 'create':
        p.set_usage("\n\t%prog create GALAXY_URL EMAIL [PUBLIC_NAME]"
                    "\n\t%prog create GALAXY_URL -t TEMPLATE START [END]"
                    "\n\t%prog create GALAXY_URL -b FILE [options]")
        p.add_option('-p','--password',action='store',dest='passwd',
                     default=None,
                     help="specify password for new user account "
                     "(otherwise program will prompt for password)")
        p.add_option('-c','--check',action='store_true',dest='check',
                     default=False,
                     help="check user details but don't try to create "
                     "the new account")
        p.add_option('-t','--template',action='store_true',
                     dest='template',default=False,
                     help="indicates that EMAIL is actually a "
                     "'template' email address which includes a '#' "
                     "symbol as a placeholder where an integer index "
                     "should be substituted to make multiple accounts "
                     "(e.g. 'student#@galaxy.ac.uk').")
        p.add_option('-b','--batch',action='store_true',dest='batch',
                     default=False,
                     help="create multiple users reading details from "
                     "TSV file (columns should be: "
                     "email,password[,public_name])")
        p.add_option('-m','--message',action='store',
                     dest='message_template',default=None,
                     help="populate and output Mako template "
                     "MESSAGE_TEMPLATE")
        
    # Process remaining arguments on command line
    if args[1] in ('-h','--help','--version'):
        args = args[1:]
    else:
        args = args[2:]
    options,args = p.parse_args(args)
    handle_debug(debug=options.debug)
    handle_suppress_warnings(suppress_warnings=options.suppress_warnings)
    handle_ssl_warnings(verify=(not options.no_verify))

    # Handle password if required
    email,password = handle_credentials(options.username,
                                        options.galaxy_password,
                                        prompt="Password for %s: " % galaxy_url)

    # Get a Galaxy instance
    gi = get_galaxy_instance(galaxy_url,api_key=options.api_key,
                             email=email,password=password,
                             verify_ssl=(not options.no_verify))
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)

    # Execute command
    if command == 'list':
        users.list_users(gi,name=options.name,long_listing_format=
                         options.long_listing_format)
    elif command == 'create':
        # Check message template is .mako file
        if options.message_template:
            if not os.path.isfile(options.message_template):
                logger.critical("Message template '%s' not found"
                                % options.message_template)
                sys.exit(1)
            elif not options.message_template.endswith(".mako"):
                logger.critical("Message template '%s' is not a .mako file"
                                % options.message_template)
                sys.exit(1)
        if options.template:
            # Get the template and range of indices
            template = args[0]
            start = int(args[1])
            try:
                end = int(args[2])
            except IndexError:
                end = start
            # Create users
            retval = users.create_users_from_template(gi,template,
                                                      start,end,options.passwd,
                                                      only_check=options.check)
        elif options.batch:
            # Get the file with the user data
            tsvfile = args[0]
            # Create users
            retval = users.create_batch_of_users(gi,tsvfile,
                                                 only_check=options.check,
                                                 mako_template=options.message_template)
        else:
            # Collect email and (optionally) public name
            email = args[0]
            try:
                name = args[1]
                if not users.check_username_format(name):
                    logger.critical("Invalid name: must contain only "
                                    "lower-case letters, numbers and "
                                    "'-'")
                    sys.exit(1)
            except IndexError:
                # No public name supplied, make from email address
                name = users.get_username_from_login(email)
            # Create user
            print "Email : %s" % email
            print "Name  : %s" % name
            retval = users.create_user(gi,email,name,options.passwd,
                                       only_check=options.check,
                                       mako_template=options.message_template)

def manage_libraries(args=None):
    """
    Implements the 'manage_libraries' utility

    """
    deprecation_warning()
    if args is None:
        args = sys.argv[1:]

    p = base_parser(usage=\
                    "\n\t%prog list GALAXY_URL [options]"
                    "\n\t%prog create_library GALAXY_URL [options] NAME"
                    "\n\t%prog create_folder GALAXY_URL [options] PATH"
                    "\n\t%prog add_datasets GALAXY_URL [options] DEST FILE...",
                    description="Manage and populate data libraries in a "
                    "Galaxy instance")
    
    commands = ['list','create_library','create_folder','add_datasets']

    # Get compulsory arguments
    if len(args) == 1:
        if args[0] == '-h' or args[0] == '--help':
            p.print_usage()
        elif args[0] == '--version':
            p.print_version()
        sys.exit(0)
    if len(args) < 2:
        p.error("need to supply a command and a Galaxy URL/alias")
    command = args[0]
    galaxy_url = args[1]

    # Setup additional command line options
    if command not in commands:
        p.error("unrecognised command: '%s'" % command)
    elif command == 'list':
        p.set_usage("%prog list GALAXY_URL [options]")
        p.add_option('-l',action='store_true',
                     dest='long_listing_format',default=False,
                     help="use a long listing format (include ids, "
                     "descriptions and file sizes and paths)")
    elif command == 'create_library':
        p.set_usage("%prog create_library GALAXY_URL [options] NAME")
        p.add_option('-d','--description',action='store',
                     dest='description',default=None,
                     help="optional description")
        p.add_option('-s','--synopsis',action='store',dest='synopsis',
                     default=None,help="optional synopsis")
    elif command == 'create_folder':
        p.set_usage("%prog create_folder GALAXY_URL [options] PATH")
        p.add_option('-d','--description',action='store',
                     dest='description',default=None,
                     help="optional description")
    elif command == 'add_datasets':
        p.set_usage("%prog add_datasets GALAXY_URL [options] DEST FILE...")
        p.add_option('--server',action='store_true',dest='from_server',
                     default=False,
                     help="upload files from Galaxy server file system "
                     "paths (default is to upload files from local "
                     "system)")
        p.add_option('--link',action='store_true',dest='link',
                     default=False,
                     help="create symlinks to files on server (only "
                     "valid if used with --server; default is to copy "
                     "files into Galaxy)")
        p.add_option('--dbkey',action='store',dest='dbkey',default='?',
                     help="dbkey to assign to files (default is '?')")
        p.add_option('--file_type',action='store',dest='file_type',
                     default='auto',
                     help="file type to assign to files (default is "
                     "'auto')")

    # Process remaining arguments on command line
    if args[1] in ('-h','--help','--version'):
        args = args[1:]
    else:
        args = args[2:]
    options,args = p.parse_args(args)
    handle_debug(debug=options.debug)
    handle_suppress_warnings(suppress_warnings=options.suppress_warnings)
    handle_ssl_warnings(verify=(not options.no_verify))

    # Handle password if required
    email,password = handle_credentials(options.username,
                                        options.galaxy_password,
                                        prompt="Password for %s: " % galaxy_url)

    # Get a Galaxy instance
    gi = get_galaxy_instance(galaxy_url,api_key=options.api_key,
                             email=email,password=password,
                             verify_ssl=(not options.no_verify))
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)

    # Execute command
    if command == 'list':
        if len(args) == 1:
            # List folders in data library
            libraries.list_library_contents(gi,args[0],long_listing_format=
                                            options.long_listing_format)
        else:
            # List data libraries
            libraries.list_data_libraries(gi)
    elif command == 'create_library':
        # Create a new data library
        if len(args) == 1:
            libraries.create_library(gi,args[0],
                                     description=options.description,
                                     synopsis=options.synopsis)
        else:
            p.error("Usage: create_library NAME")
    elif command == 'create_folder':
        # Create a new folder data library
        if len(args) == 1:
            libraries.create_folder(gi,args[0],
                                    description=options.description)
        else:
            p.error("Usage: create_folder PATH")
    elif command == 'add_datasets':
        # Add a dataset to a library
        if len(args) < 2:
            p.error("Usage: add_datasets DEST FILE [FILE...]")
        libraries.add_library_datasets(gi,args[0],args[1:],
                                       from_server=options.from_server,
                                       link_only=options.link,
                                       file_type=options.file_type,
                                       dbkey=options.dbkey)
 
def manage_tools(args=None):
    """
    Implements the 'manage_tools' utility

    """
    deprecation_warning()
    if args is None:
        args = sys.argv[1:]

    p = base_parser(usage=\
                    "\n\t%prog list GALAXY_URL [options]"
                    "\n\t%prog installed GALAXY_URL [options]"
                    "\n\t%prog tool_panel GALAXY_URL [options]"
                    "\n\t%prog install GALAXY_URL [options] SHED OWNER TOOL [REVISION]"
                    "\n\t%prog update GALAXY_URL [options] SHED OWNER TOOL",
                    description="Manage and install tools in a Galaxy "
                    "instance")
    
    commands = ['list','installed','tool_panel','install','update']

    # Get compulsory arguments
    if len(args) == 1:
        if args[0] == '-h' or args[0] == '--help':
            p.print_usage()
        elif args[0] == '--version':
            p.print_version()
        sys.exit(0)
    if len(args) < 2:
        p.error("need to supply a command and a Galaxy URL/alias")
    command = args[0]
    galaxy_url = args[1]

    # Setup additional command line options
    if command not in commands:
        p.error("unrecognised command: '%s'" % command)
    elif command == 'list':
        p.set_usage("%prog list GALAXY_URL [options]")
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific tool name(s) to list")
        p.add_option('--installed',action='store_true',
                     dest='installed_only',default=False,
                     help="only list tools installed from a toolshed")
    elif command == 'installed':
        p.set_usage("%prog installed GALAXY_URL [options]")
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific tool repository/ies to list")
        p.add_option('--toolshed',action='store',dest='toolshed',default=None,
                     help="only list repositories from TOOLSHED")
        p.add_option('--owner',action='store',dest='owner',default=None,
                     help="only list repositories owned by OWNER")
        p.add_option('--list-tools',action='store_true',dest='list_tools',
                     default=None,
                     help="list the associated tools for each repository")
        p.add_option('--updateable',action='store_true',dest='updateable',
                     default=None,
                     help="only show repositories with uninstalled updates "
                     "or upgrades")
    elif command == 'tool_panel':
        p.set_usage("%prog tool_panel GALAXY_URL [options]")
        p.add_option('--name',action='store',dest='name',default=None,
                     help="specific tool panel section(s) to list")
        p.add_option('--list-tools',action='store_true',dest='list_tools',
                     default=None,
                     help="list the associated tools for each section")
    elif command == 'install':
        p.set_usage("%prog install GALAXY_URL [options] SHED OWNER TOOL "
                    "[REVISION]")
        p.add_option('--tool-panel-section',action='store',
                     dest='tool_panel_section',default=None,
                     help="tool panel section name or id to install the "
                     "tool under")
    elif command == 'update':
        p.set_usage("%prog update GALAXY_URL [options] SHED OWNER TOOL")

    # Process remaining arguments on command line
    if args[1] in ('-h','--help','--version'):
        args = args[1:]
    else:
        args = args[2:]
    options,args = p.parse_args(args)
    handle_debug(debug=options.debug)
    handle_suppress_warnings(suppress_warnings=options.suppress_warnings)
    handle_ssl_warnings(verify=(not options.no_verify))

    # Handle password if required
    email,password = handle_credentials(options.username,
                                        options.galaxy_password,
                                        prompt="Password for %s: " % galaxy_url)

    # Get a Galaxy instance
    gi = get_galaxy_instance(galaxy_url,api_key=options.api_key,
                             email=email,password=password,
                             verify_ssl=(not options.no_verify))
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)

    # Execute command
    if command == 'list':
        tools.list_tools(gi,name=options.name,
                         installed_only=options.installed_only)
    elif command == 'installed':
        tools.list_installed_repositories(gi,name=options.name,
                                          toolshed=options.toolshed,
                                          owner=options.owner,
                                          list_tools=options.list_tools,
                                          only_updateable=options.updateable)
    elif command == 'tool_panel':
        tools.list_tool_panel(gi,name=options.name,
                              list_tools=options.list_tools)
    elif command == 'install':
        if len(args) < 3:
            p.error("Need to supply toolshed, owner, repo and optional "
                    "revision")
        toolshed,owner,repo = args[:3]
        if len(args) == 4:
            revision = args[3]
        else:
            revision = None
        status = tools.install_tool(
            gi,toolshed,repo,owner,revision=revision,
            tool_panel_section=options.tool_panel_section)
        sys.exit(status)
    elif command == 'update':
        if len(args) != 3:
            p.error("Need to supply toolshed, owner and repo")
        toolshed,owner,repo = args[:3]
        status = tools.update_tool(gi,toolshed,repo,owner)
        sys.exit(status)
