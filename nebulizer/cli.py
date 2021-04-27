#!/usr/bin/env python
#
# cli: functions for building command utilities
import sys
import getpass
import logging
import click
import time
import fnmatch
from nebulizer import get_version
from .core import get_galaxy_instance
from .core import get_current_user
from .core import get_galaxy_config
from .core import ping_galaxy_instance
from .core import prompt_for_confirmation
from .core import turn_off_urllib3_warnings
from .core import Credentials
from .core import Reporter
from . import options
from . import users
from . import libraries
from . import tools
from . import search
from .quotas import handle_quota_spec
from .quotas import list_quotas
from .quotas import create_quota
from .quotas import update_quota
from .quotas import delete_quota

# Initialise logging
logger = logging.getLogger(__name__)
# Suppress errors from bioblend
logging.getLogger("bioblend").setLevel(logging.CRITICAL)

def handle_ssl_warnings(verify=True):
    """
    Turn off SSL warnings from urllib3

    Arguments:
      verify (bool): if False then disable the warnings from
        urllib3 about SSL certificate verification

    """
    if not verify:
        logger.warning("SSL certificate verification has "
                       "been disabled")
        turn_off_urllib3_warnings()

def handle_debug(debug=True):
    """
    Turn on debugging output from logging

    Arguments:
      debug (bool): if True then turn on debugging output

    """
    if debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.getLogger("nebulizer").setLevel(level)

def handle_suppress_warnings(suppress_warnings=True):
    """
    Suppress warning messages output from logging

    Arguments:
      suppress_warnings (bool): if True then turn off
        warning messages

    """
    if suppress_warnings:
        logging.getLogger("nebulizer").setLevel(logging.ERROR)

def handle_credentials(email,password,prompt="Password: "):
    """
    Sort out email and password for accessing Galaxy

    Arguments:
      email (str): Galaxy e-mail address corresponding to the user
      password (str): password of Galaxy account corresponding to
        email address; if None then user will be prompted to
        supply password on the command line
      prompt (str): text to display as password prompt

    Returns:
      Tuple: tuple consisting of (email,password).

    """
    if email is None:
        return (None,None)
    if password is None:
        password = getpass.getpass(prompt)
    return (email,password)

def fetch_new_api_key(galaxy_url,email,password=None,verify=True):
    """
    Fetch a new API key from a Galaxy instance

    Arguments:
      galaxy_url (str): alias or URL of Galaxy instance to get
        API key for
      email (str): Galaxy e-mail address corresponding to the
        user to fetch API for
      password (str): password of Galaxy account corresponding to
        email address (optional)
      verify (boolean): if False then disable SSL verification
        when connecting to Galaxy instance (default is to keep
        SSL verification)

    """
    print("Fetching API key from %s" % galaxy_url)
    email,password = handle_credentials(
        email,password,
        prompt="Please supply password for %s: " % galaxy_url)
    gi = get_galaxy_instance(galaxy_url,
                             email=email,password=password,
                             verify_ssl=verify)
    return users.get_user_api_key(gi,username=email)

class Context:
    """
    Provide context for nebulizer command
    """
    def __init__(self):
        self.api_key = None
        self.username = None
        self.galaxy_password = None
        self.no_verify = False
        self.debug = False

    def galaxy_instance(self,alias,validate_key=True):
        """
        Return Galaxy instance based on context

        Attempts to create a Bioblend based on the supplied
        arguments to the nebulizer command.
        """
        email,password = handle_credentials(
            self.username,
            self.galaxy_password,
            prompt="Password for %s: " % alias)
        gi = get_galaxy_instance(alias,api_key=self.api_key,
                                 email=email,password=password,
                                 validate_key=validate_key,
                                 verify_ssl=(not self.no_verify))
        return gi

pass_context = click.make_pass_decorator(Context,ensure=True)

@click.group()
@click.version_option(version=get_version())
@click.option('--api_key','-k',
              help="specify API key to use for connecting to "
              "Galaxy instance. Must be supplied if there is "
              "no API key stored for the specified instance, "
              "(unless --username option is specified). If "
              "there is a stored API key this overrides it.")
@click.option('--username','-u',
              help="specify username (i.e. email) for connecting "
              "to Galaxy instance, as an alternative to using "
              "the API key. Prompts for a password unless one "
              "is supplied via the --galaxy_password option.")
@click.option('--galaxy_password','-P',
              help="supply password for connecting to Galaxy "
              "instance, when using the --username option.")
@click.option('--no-verify','-n',is_flag=True,
              help="don't verify HTTPS connections when "
              "connecting to Galaxy instance. Use this when "
              "interacting with Galaxy instances which use "
              "self-signed certificates.")
@click.option('--suppress-warnings','-q',is_flag=True,
              help="suppress warning messages from nebulizer.")
@click.option('--debug',is_flag=True,
              help="turn on debugging output.")
@pass_context
def nebulizer(context,api_key,username,galaxy_password,
              no_verify,suppress_warnings,debug):
    """
    Manage users, tools and data libraries in Galaxy instances
    via the API
    """
    context.api_key = api_key
    context.username = username
    context.galaxy_password = galaxy_password
    context.no_verify = no_verify
    context.debug = debug
    context.suppress_warnings = suppress_warnings
    handle_debug(debug=context.debug)
    handle_suppress_warnings(suppress_warnings=context.suppress_warnings)
    handle_ssl_warnings(verify=(not context.no_verify))

@nebulizer.command(name="list_keys")
@click.option("--name",
              help="list only aliases matching name. Can "
              "include glob-style wild-cards.")
@click.option("-s","--show-api-keys",is_flag=True,
              help="show the API key string associated with "
              "each alias")
@pass_context
def list_keys(context,name,show_api_keys=False):
    """
    List stored Galaxy API key aliases.

    Prints a list of stored aliases with the associated
    Galaxy URLs; optionally also show the API key string.
    """
    instances = Credentials()
    aliases = instances.list_keys()
    if name:
        name = name.lower()
        aliases = [alias for alias in aliases
                   if fnmatch.fnmatch(alias.lower(),name)]
    output = Reporter()
    for alias in aliases:
        galaxy_url,api_key = instances.fetch_key(alias)
        display_items = [alias,galaxy_url]
        if show_api_keys:
            display_items.append(api_key)
        output.append(display_items)
    output.report()

@nebulizer.command(name="add_key")
@click.argument("alias")
@click.argument("galaxy_url")
@click.argument("api_key",required=False)
@pass_context
def add_key(context,alias,galaxy_url,api_key=None):
    """
    Store new Galaxy URL and API key.

    ALIAS is the name that the instance will be stored
    against; GALAXY_URL is the URL for the instance;
    API_KEY is the corresponding API key.

    If API_KEY is not supplied then nebulizer will
    attempt to fetch one automatically.
    """
    instances = Credentials()
    if alias in instances.list_keys():
        logger.error("'%s' already exists" % alias)
        sys.exit(1)
    if api_key is None:
        # No API key supplied as argument, try to connect
        # to Galaxy and fetch directly
        gi = context.galaxy_instance(galaxy_url)
        if gi is None:
            logger.fatal("%s: failed to connect" % galaxy_url)
            sys.exit(1)
        api_key = gi.key
    # Store the entry
    if not instances.store_key(alias,galaxy_url,api_key):
        sys.exit(1)

@nebulizer.command(name="update_key")
@click.option('--new-url',
              help="specify new URL for Galaxy instance")
@click.option('--new-api-key',
              help="specify new API key for Galaxy instance")
@click.option('--fetch-api-key',is_flag=True,
              help="fetch new API key for Galaxy instance")
@click.argument("alias")
@pass_context
def update_key(context,alias,new_url,new_api_key,fetch_api_key):
    """
    Update stored Galaxy API key.

    Update the Galaxy URL and/or API key stored
    against ALIAS.
    """
    instances = Credentials()
    if alias not in instances.list_keys():
        logger.error("'%s': not found" % alias)
        sys.exit(1)
    if new_url:
        galaxy_url = new_url
    else:
        galaxy_url = instances.fetch_key(alias)[0]
    click.echo("galaxy_url: %s" % galaxy_url)
    click.echo("username  : %s" % context.username)
    if fetch_api_key:
        # Attempt to connect to Galaxy and fetch API key
        gi = context.galaxy_instance(alias)
        if gi is None:
            logger.critical("%s: failed to connect" % alias)
            sys.exit(1)
        new_api_key = gi.key
    if not instances.update_key(alias,
                                new_url=new_url,
                                new_api_key=new_api_key):
        sys.exit(1)

@nebulizer.command(name="remove_key")
@click.argument("alias")
@pass_context
def remove_key(context,alias):
    """
    Remove stored Galaxy API key.

    Removes the Galaxy URL/API key pair associated with
    ALIAS from the list of stored keys.
    """
    instances = Credentials()
    if not instances.has_key(alias):
        logger.fatal("No alias '%s' to remove" % alias)
        sys.exit(1)
    print("Removing key for alias '%s'" % alias)
    if prompt_for_confirmation("Proceed?"):
        if not instances.remove_key(alias):
            sys.exit(1)

@nebulizer.command(name="list_users")
@click.option("--name",
              help="list only users with matching email or user "
              "name. Can include glob-style wild-cards.")
@click.option("--status",
              type=click.Choice(['active','deleted','purged','all']),
              default='active',
              help="list users with the specified status; can be "
              "one of 'active', 'deleted', 'purged', 'all' "
              "(default: 'active')")
@click.option("--long","-l","long_listing",is_flag=True,
              help="use a long listing format that includes ids,"
              " disk usage and admin status.")
@click.option("--sort",
              default='email',
              help="comma-separated list of fields to output on; "
              "valid fields are 'email', 'disk_usage', 'quota', "
              "'quota_usage' (default: 'email').")
@click.option("--show_id",is_flag=True,
              help="include internal Galaxy user ID.")
@click.argument("galaxy")
@pass_context
def list_users(context,galaxy,name,status,long_listing,sort,show_id):
    """
    List users in Galaxy instance.

    Prints details of user accounts in GALAXY instance.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Turn sort keys into a list
    sort_keys = sort.split(',')
    for key in sort_keys:
        if key not in ('email','disk_usage','quota','quota_usage'):
            logger.fatal("'%s': invalid sort key" % key)
            sys.exit(1)
    # List users
    sys.exit(users.list_users(gi,name=name,
                              long_listing_format=long_listing,
                              sort_by=sort_keys,
                              status=status,
                              show_id=show_id))

@nebulizer.command(name="create_user")
@click.option('--password','-p',
              help="specify password for new user account "
              "(otherwise program will prompt for password)")
@click.option('--check','-c','only_check',is_flag=True,
              help="check user details but don't try to create the "
              "new account")
@click.option('--message','-m','message_template',
              type=click.Path(exists=True),
              help="Mako template to populate and output")
@click.argument("galaxy")
@click.argument("email")
@click.argument("public_name",required=False)
@pass_context
def create_user(context,galaxy,email,public_name,password,only_check,
                message_template):
    """
    Create new Galaxy user.

    Creates a new user in GALAXY, using EMAIL for the username.
    If PUBLIC_NAME is not supplied then it will be generated
    automatically from the leading part of the email address.

    If a password for the new account is not supplied using the
    --password option then nebulizer will prompt for one.
    """
    # Check message template is a .mako file
    if message_template:
        if not message_template.endswith(".mako"):
            logger.critical("Message template '%s' is not a .mako file"
                            % message_template)
            sys.exit(1)
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Sort out email and public name
    if public_name:
        if not users.check_username_format(public_name):
            logger.critical("Invalid public name: must contain only "
                            "lower-case letters, numbers and '-'")
            sys.exit(1)
    else:
        # No public name supplied, make from email address
        public_name = users.get_username_from_login(email)
    # Create user
    print("Email : %s" % email)
    print("Name  : %s" % public_name)
    sys.exit(users.create_user(gi,email,public_name,password,
                               only_check=only_check,
                               mako_template=message_template))

@nebulizer.command(name="create_batch_users")
@click.option('--password','-p',
              help="specify password for new user accounts "
              "(otherwise program will prompt for password). "
              "All accounts will be created with the same "
              "password.")
@click.option('--check','-c','only_check',is_flag=True,
              help="check user details but don't try to create "
              "the new account.")
@click.argument("galaxy")
@click.argument("template")
@click.argument("start",type=int)
@click.argument("end",type=int,required=False)
@pass_context
def create_batch_users(context,galaxy,template,start,end,
                       password,only_check):
    """
    Create multiple Galaxy users from a template.

    Creates a batch of users in GALAXY using TEMPLATE; this
    should be a template email address which includes a
    '#' symbol as a placeholder for an integer index.

    The range of integers is defined by START and END; if
    only one of these is supplied then START is assumed to be
    1 and the supplied value is END.

    For example: using the template 'user#@example.org'
    with the range 1 to 5 will create new accounts:

    user1@galaxy.org
    ...
    user5@galaxy.org
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Sort out start and end indices
    if end is None:
        end = start
        start = 1
    # Create users
    sys.exit(users.create_users_from_template(gi,template,
                                              start,end,password,
                                              only_check=only_check))

@nebulizer.command(name="create_users_from_file")
@click.option('--check','-c','only_check',is_flag=True,
              help="check user details but don't try to create the "
              "new account.")
@click.option('--message','-m','message_template',
              type=click.Path(exists=True),
              help="Mako template to populate and output.")
@click.argument("galaxy")
@click.argument("file",type=click.Path(exists=True))
@pass_context
def create_users_from_file(context,galaxy,file,message_template,
                           only_check):
    """
    Create multiple Galaxy users from a file.

    Creates user accounts in GALAXY instance from contents of
    FILE, which should be a tab-delimited file with details of
    a new user on each line; the columns should be 'email',
    'password', and optionally 'public_name'.

    (If the 'public_name' is missing then it will be generated
    automatically from the leading part of the email.)
    """
    # Check message template is a .mako file
    if message_template:
        if not message_template.endswith(".mako"):
            logger.critical("Message template '%s' is not a .mako file"
                            % message_template)
            sys.exit(1)
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Create users
    sys.exit(users.create_batch_of_users(gi,file,
                                         only_check=only_check,
                                         mako_template=message_template))

@nebulizer.command(name="delete_user")
@click.argument("galaxy")
@click.argument("email")
@click.option('-p','--purge',is_flag=True,
              help="also purge (permanently delete) the user.")
@click.option('-y','--yes',is_flag=True,
              help="don't ask for confirmation of deletions.")
@pass_context
def delete_user(context,galaxy,email,purge,yes):
    """
    Delete a user account from a Galaxy instance

    Removes user account with username EMAIL from GALAXY.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    sys.exit(users.delete_user(gi,email,purge=purge,no_confirm=yes))

@nebulizer.command(name="list_tools")
@click.option('--name',metavar='NAME',
              help="only list tool repositories matching NAME. Can "
              "include glob-style wild-cards.")
@click.option('--toolshed',metavar='TOOLSHED',
              help="only list repositories installed from toolshed "
              "matching TOOLSHED. Can include glob-style wild-cards.")
@click.option('--owner',metavar='OWNER',
              help="only list repositories from matching OWNER. "
              "Can include glob-style wild-cards.")
@click.option('--updateable',is_flag=True,
              help="only show repositories with uninstalled updates "
              "or upgrades.")
@click.option('--built-in',is_flag=True,
              help="include built-in tools.")
@click.option('--mode',
              type=click.Choice(['repos','tools','export']),
              default='repos',
              help="set reporting mode: either 'repos' "
              "(repository-centric view, the default), 'tools' "
              "(tool-centric view) or 'export' (tab-delimited "
              "format for use with 'install_tool').")
@click.option('--check-toolshed',is_flag=True,
              help="check installed revisions directly against those "
              "available in the toolshed. NB this can be extremely "
              "slow.")
@click.argument("galaxy")
@pass_context
def list_tools(context,galaxy,name,toolshed,owner,updateable,built_in,
               mode,check_toolshed):
    """
    List information about tools and installed tool repositories.

    Prints details of the tools and installed tool repositories in
    GALAXY instance.

    In the default 'repository-centric' mode, the installed tool
    repositories are listed with details including: repository
    name, toolshed, owner, revision id and changeset, and
    installation status.

    Repository details are also preceeded by a single-character
    'status' indicator ('D' = deprecated; '^' = newer revision
    installed; 'u' = update available but not installed; 'U' =
    upgrade available but not installed; '*' = latest revision).

    (Note that there may still be a newer revision of a tool
    available from the toolshed, even when the repository is
    marked as '*'. Use the --check-toolshed option to also
    explicitly check against the toolshed, in which case a '!'
    status indicates that a newer version has been found on
    toolshed. Note that this option incurs a significant overhead
    when checking a large number of tools.)

    Different reporting modes are available: the default is a
    'repository-centric' mode, alternatively a 'tool-centric'
    mode (which lists tools according to their names as they appear
    in the Galaxy tool panel) and an 'export' mode (which produces
    output suitable for use with 'install_tool') are also available.
    The --mode option is used to switch between the default 'repos'
    mode and the alternative 'tools' and 'export' modes.

    In export mode the output is a set of tab-delimited values, with
    each line consisting of:

    TOOLSHED|OWNER|REPOSITORY|CHANGESET|TOOL_PANEL_SECTION

    If the --built-in option is specified then built-in tools
    (i.e. tools not installed from a toolshed) will also be
    included. (NB this option is ignored in 'export' mode.)
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # List repositories
    sys.exit(tools.list_tools(
        gi,name=name,
        tool_shed=toolshed,
        owner=owner,
        include_builtin=built_in,
        mode=mode,
        only_updateable=updateable,
        check_tool_shed=check_toolshed))

@nebulizer.command(name="list_tool_panel")
@click.option('--name',metavar='NAME',
              help="only list tool panel sections where name or "
              "id match NAME. Can include glob-style wild-cards.")
@click.option('--list-tools',is_flag=True,
              help="also list the associated tools for each "
              "section")
@click.argument("galaxy")
@pass_context
def list_tool_panel(context,galaxy,name,list_tools):
    """
    List tool panel contents.

    Prints details of tool panel sections including the
    displayed text and the internal section id, and any
    tools available outside of any section.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # List tool panel contents
    sys.exit(tools.list_tool_panel(gi,name=name,
                                   list_tools=list_tools))

@nebulizer.command(name="install_tool")
@click.option('--tool-panel-section',
              help="tool panel section name or id to install "
              "the tool under; if the section doesn't exist "
              "then it will be created. If this option is "
              "omitted then the tool will be installed at the "
              "top-level i.e. not in any section.")
@options.install_tool_dependencies_option(default='yes')
@options.install_repository_dependencies_option(default='yes')
@options.install_resolver_dependencies_option(default='yes')
@click.option('--file',metavar='TSV_FILE',
              type=click.File('rt'),
              help="install tools specified in TSV_FILE.")
@click.option('--timeout',metavar='TIMEOUT',default=600,
              help="wait up to TIMEOUT seconds for tool installations"
              "to complete (default is 600).")
@click.option('--no-wait',is_flag=True,
              help="don't wait for lengthy tool installations to "
              "complete.")
@click.option('-y','--yes',is_flag=True,
              help="don't ask for confirmation of installation.")
@click.argument("galaxy")
@click.argument("repository",nargs=-1)
@pass_context
def install_tool(context,galaxy,repository,tool_panel_section,
                 install_tool_dependencies,
                 install_repository_dependencies,
                 install_resolver_dependencies,
                 file,timeout,no_wait,yes):
    """
    Install tool(s) from toolshed.

    Installs the specified tool from REPOSITORY into GALAXY,
    where REPOSITORY can be as one of:

    - full URL including the revision e.g.
    https://toolshed.g2.bx.psu.edu/view/devteam/fastqc/e7b2202befea

    - full URL without revision e.g.
    https://toolshed.g2.bx.psu.edu/view/devteam/fastqc

    - OWNER/TOOLNAME combination e.g. devteam/fastqc
    (toolshed is assumed to be main Galaxy toolshed)

    - [ TOOLSHED ] OWNER TOOLNAME [ REVISION ] e.g.
    https://toolshed.g2.bx.psu.edu devteam fastqc

    If a changeset REVISION isn't specified then the
    latest revision will be assumed.

    Installation will fail if the specified revision is
    not installable, or if no installable revisions are
    found.

    Alternatively multiple tools can be installed in a
    single invocation of the command by specifying the
    --file option instead of a repository, in which case
    TSV_FILE should be a tab-delimited file with the
    columns:

    TOOLSHED|OWNER|REPOSITORY|REVISON|SECTION

    (This is the format generated by 'list_tools
    --mode=export'.)

    If the REVISION field is blank then nebulizer will
    attempt to install the latest revision; if the
    SECTION field is blank then the tool will be
    installed at the top level of the tool panel (i.e.
    not in any section).
    """
    if repository:
        # Single repository specification
        try:
            toolshed,owner,repository,revision = \
                tools.handle_repository_spec(repository)
        except Exception as ex:
            logger.fatal(ex)
            sys.exit(1)
    else:
        if file is None:
            logger.fatal("Need to supply either a repository "
                         "spec or a file (via --file)")
            sys.exit(1)
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Install tool(s)
    if repository:
        # Single repository
        sys.exit(tools.install_tool(
            gi,toolshed,repository,owner,revision=revision,
            tool_panel_section=tool_panel_section,
            timeout=timeout,no_wait=no_wait,
            install_tool_dependencies=
            (install_tool_dependencies == 'yes'),
            install_repository_dependencies=
            (install_repository_dependencies== 'yes'),
            install_resolver_dependencies=
            (install_resolver_dependencies== 'yes'),
            no_confirm=yes))
    else:
        # Multiple repositories from the file
        failed_install = []
        # Install tools
        for line in file:
            if line.startswith('#'):
                continue
            print(line.rstrip('\n'))
            line = line.rstrip('\n').split('\t')
            try:
                toolshed,owner,repository = [x.strip() for x in line[:3]]
            except ValueError:
                logger.critical("Couldn't parse line")
                sys.exit(1)
            try:
                revision = line[3]
                if not revision:
                    revision = None
            except IndexError:
                revision = None
            try:
                tool_panel_section = line[4]
                if not tool_panel_section:
                    tool_panel_section = None
            except IndexError:
                tool_panel_section = None
            status = tools.install_tool(
                gi,toolshed,repository,owner,revision=revision,
                tool_panel_section=tool_panel_section,
                timeout=timeout,no_wait=no_wait,
                install_tool_dependencies=
                (install_tool_dependencies == 'yes'),
                install_repository_dependencies=
                (install_repository_dependencies== 'yes'),
                install_resolver_dependencies=
                (install_resolver_dependencies== 'yes'),
                no_confirm=yes)
            if status != tools.TOOL_INSTALL_OK:
                failed_install.append(line)
        # List any failed tool installations
        if failed_install:
            logger.error("Some requested tool repositories couldn't be "
                         "installed")
            for repo in failed_install:
                click.echo('\t'.join(repo))
            sys.exit(1)
        # Looks like everything worked
        sys.exit(0)

@nebulizer.command(name="update_tool")
@options.install_tool_dependencies_option(default='yes')
@options.install_repository_dependencies_option(default='yes')
@options.install_resolver_dependencies_option(default='yes')
@click.option('--timeout',metavar='TIMEOUT',default=600,
              help="wait up to TIMEOUT seconds for tool installations"
              "to complete (default is 600).")
@click.option('--no-wait',is_flag=True,
              help="don't wait for lengthy tool installations to "
              "complete.")
@click.option('--check-toolshed',is_flag=True,
              help="check installed revisions directly against those "
              "available in the toolshed.")
@click.option('-y','--yes',is_flag=True,
              help="don't ask for confirmation of updates.")
@click.argument("galaxy")
@click.argument("repository",nargs=-1)
@pass_context
def update_tool(context,galaxy,repository,
                install_tool_dependencies,
                install_repository_dependencies,
                install_resolver_dependencies,
                timeout,no_wait,check_toolshed,
                yes):
    """
    Update tool installed from toolshed.

    Updates the specified tool from REPOSITORY into GALAXY,
    where REPOSITORY can be as one of:

    - full URL (without revision) e.g.
    https://toolshed.g2.bx.psu.edu/view/devteam/fastqc

    - OWNER/TOOLNAME combination e.g. devteam/fastqc
    (toolshed is assumed to be main Galaxy toolshed)

    - [ TOOLSHED ] OWNER TOOLNAME e.g.
    https://toolshed.g2.bx.psu.edu devteam fastqc

    OWNER and TOOLNAME can include glob-style wildcards;
    use '*/*' to update all tools.

    The tool must already be present in GALAXY and a newer
    changeset revision must be available. The update will
    be installed into the same tool panel section as the
    original tool.
    """
    # Get the tool repository details
    try:
        toolshed,owner,repository,revision = \
            tools.handle_repository_spec(repository)
    except Exception as ex:
        logger.fatal(ex)
        sys.exit(1)
    print(f"Updating {owner}/{repository} from {toolshed}")
    if revision is not None:
        logger.fatal("A revision ('%s') was also supplied "
                     "but this is not valid for tool update "
                     % revision)
        sys.exit(1)
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Install tool
    sys.exit(tools.update_tool(gi,toolshed,repository,owner,
                               timeout=timeout,no_wait=no_wait,
                               check_tool_shed=check_toolshed,
                               install_tool_dependencies=
                               (install_tool_dependencies == 'yes'),
                               install_repository_dependencies=
                               (install_repository_dependencies== 'yes'),
                               install_resolver_dependencies=
                               (install_resolver_dependencies== 'yes'),
                               no_confirm=yes))

@nebulizer.command(name="uninstall_tool")
@click.option('--remove_from_disk',is_flag=True,
              help="remove the uninstalled tool from disk (otherwise "
              "tool is just deactivated).")
@click.option('-y','--yes',is_flag=True,
              help="don't ask for confirmation of uninstallation.")
@click.argument("galaxy")
@click.argument("repository",nargs=-1)
@pass_context
def uninstall_tool(context,galaxy,repository,remove_from_disk,
                   yes):
    """
    Uninstall previously installed tool.

    Uninstalls the specified tool which was previously
    installed from REPOSITORY into GALAXY, where
    REPOSITORY can be as one of:

    - full URL (without revision) e.g.
    https://toolshed.g2.bx.psu.edu/view/devteam/fastqc

    - OWNER/TOOLNAME combination e.g. devteam/fastqc
    (toolshed is assumed to be main Galaxy toolshed)

    - [ TOOLSHED ] OWNER TOOLNAME e.g.
    https://toolshed.g2.bx.psu.edu devteam fastqc

    The tool must already be present in GALAXY; a
    revision must be specified if more than one
    revision is installed (use '*' to match all
    revisions).
    """
    # Get the tool repository details
    try:
        toolshed,owner,repository,revision = \
            tools.handle_repository_spec(repository)
    except Exception as ex:
        logger.fatal(ex)
        sys.exit(1)
    print("Uninstalling {}/{}{} from {}".format(repository,
                                            owner,
                                            '/%s' % revision
                                            if revision is not None
                                            else '',
                                            toolshed))
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Uninstall tool
    sys.exit(tools.uninstall_tool(gi,toolshed,repository,owner,revision,
                                  remove_from_disk=remove_from_disk,
                                  no_confirm=yes))

@nebulizer.command(name="search_toolshed")
@click.option("--toolshed",metavar='TOOLSHED',
              help="specify a toolshed URL to search, or 'main' "
              "(the main Galaxy toolshed, the default) or 'test' "
              "(the test Galaxy toolshed)")
@click.option('--galaxy',metavar='GALAXY',
              help="check if tool repositories are installed in "
              "GALAXY instance")
@click.option('-l','long_listing',is_flag=True,
              help="use a long listing format that includes "
              "tool descriptions")
@click.argument("query_string")
@pass_context
def search_toolshed(context,toolshed,query_string,galaxy,long_listing):
    """
    Search for repositories on a Galaxy toolshed.

    Searches for repositories on the main Galaxy toolshed
    using the specified QUERY_STRING.

    Specify other toolsheds by an alias (either 'main' or
    'test') or by supplying the shed URL.

    If a GALAXY instance is supplied then also check
    whether the tool repositories are already installed.
    """
    # Determine the toolshed
    if toolshed is None:
        # Default to the main Galaxy toolshed
        toolshed = "main"
    if toolshed == "main":
        toolshed = "https://toolshed.g2.bx.psu.edu/"
    elif toolshed == "test":
        toolshed = "https://testtoolshed.g2.bx.psu.edu/"
    # Get a Galaxy instance, if specified
    if galaxy is not None:
        gi = context.galaxy_instance(galaxy)
        if gi is None:
            logger.critical("Failed to connect to Galaxy instance")
            sys.exit(1)
    else:
        gi = None
    # Search the toolshed
    sys.exit(search.search_toolshed(toolshed,query_string,gi=gi,
                                    long_listing_format=long_listing))

@nebulizer.command(name="list_libraries")
@click.option('-l','long_listing',is_flag=True,
              help="use a long listing format that includes "
              "descriptions, file sizes, dbkeys and paths)")
@click.option('--show_id',is_flag=True,
              help="include internal Galaxy IDs for data "
              "libraries, folders and datasets.")
@click.argument("galaxy")
@click.argument("path",required=False)
@pass_context
def list_libraries(context,galaxy,path,long_listing,show_id):
    """
    List data libraries and contents.

    Prints details of the data library and folders
    specified by PATH, in GALAXY instance.

    PATH should be of the form
    'data_library[/folder[/subfolder[...]]]'
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # List folders in data library
    if path:
        sys.exit(libraries.list_library_contents(
            gi,path,
            long_listing_format=long_listing,
            show_id=show_id))
    else:
        sys.exit(libraries.list_data_libraries(
            gi,
            long_listing_format=long_listing,
            show_id=show_id))

@nebulizer.command(name="create_library")
@click.option('-d','--description',
              help="description of the new library")
@click.option('-s','--synopsis',
              help="synopsis text for the new library")
@click.argument("galaxy")
@click.argument("name")
@pass_context
def create_library(context,galaxy,name,description,synopsis):
    """
    Create new data library.

    Makes a new data library NAME in GALAXY. A library
    with the same name must not already.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Create new data library
    libraries.create_library(gi,name,
                             description=description,
                             synopsis=synopsis)

@nebulizer.command(name="create_library_folder")
@click.option('-d','--description',
              help="description of the new folder")
@click.argument("galaxy")
@click.argument("path")
@pass_context
def create_library_folder(context,galaxy,path,description):
    """
    Create new folder in a data library.

    Makes a new folder or folder tree within an existing data
    library in GALAXY.

    The new folder(s) are specified by PATH, which should be
    of the form 'data_library[/folder[/subfolder[...]]]'.
    Although the data library must already exist, PATH must
    not address an existing folder.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Create new folder
    if libraries.create_folder(gi,path,
                               description=description) is None:
        sys.exit(1)

@nebulizer.command(name="add_library_datasets")
@click.option('--file-type',default='auto',
              help="Galaxy data type to assign the files to "
              "(default is 'auto'). Must be a valid Galaxy "
              "data type. If not 'auto' then all files will "
              "be assigned the same type.")
@click.option('--dbkey',default='?',
              help="dbkey to assign to files (default is '?')")
@click.option('--server','from_server',is_flag=True,
              help="upload files from the Galaxy server file "
              "system (default is to upload files from local "
              "system)")
@click.option('--link',is_flag=True,
              help="create symlinks to files on server (only "
              "valid if used with --server; default is to copy "
              "files into Galaxy)")
@click.argument("galaxy")
@click.argument("dest")
@click.argument("file",nargs=-1)
@pass_context
def add_library_datasets(context,galaxy,dest,file,file_type,
                         dbkey,from_server,link):
    """
    Add datasets to a data library.

    Uploads one or more FILEs as new datasets in the
    data library folder DEST in GALAXY.

    DEST should be a path to a data library or library
    folder of the form
    'data_library[/folder[/subfolder[...]]]'. The library
    and folder must already exist.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Add the datasets
    libraries.add_library_datasets(gi,dest,file,
                                   from_server=from_server,
                                   link_only=link,
                                   file_type=file_type,
                                   dbkey=dbkey)

@nebulizer.command(name="quotas")
@click.option("--name",
              help="list only quotas with matching name. Can "
              "include glob-style wild-cards.")
@click.option("--status",
              type=click.Choice(['active','deleted','all']),
              default='active',
              help="list quotas with the specified status; can be "
              "one of 'active', 'deleted', 'all' (default: 'active')")
@click.option("--long","-l","long_listing",is_flag=True,
              help="use a long listing format that includes lists "
              "of associated users and groups.")
@click.argument("galaxy")
@pass_context
def quotas(context,galaxy,name,status,long_listing):
    """
    List quotas in Galaxy instance.

    Prints details of quotas in GALAXY instance.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # List users
    sys.exit(list_quotas(gi,name=name,
                         status=status,
                         long_listing_format=long_listing))

@nebulizer.command(name="quota_add")
@click.option('-d','--description',
              help="description of the new quota (will be "
              "the same as the NAME if not supplied).")
@click.option('--default_for',
              help="set the quota as the default for either "
              "'registered' or 'unregistered' users.")
@click.option('-u','--users',metavar="EMAIL[,EMAIL...]",
              help="list of user emails to associate with the "
              "quota, separated by commas.")
@click.option('-g','--groups',metavar="GROUP[,GROUP...]",
              help="list of group names to associate with the "
              "quota, separated by commas.")
@click.argument("galaxy")
@click.argument("name")
@click.argument("quota")
@pass_context
def quota_add(context,galaxy,name,quota,description=None,
              default_for=None,users=None,groups=None):
    """
    Create new quota.

    Makes a new quota called NAME in GALAXY. A quota with
    the same name must not already exist.

    QUOTA specifies the type of quota, and must be of the
    form

    [OPERATION][AMOUNT]

    where OPERATION is any valid operation ('=','+','-';
    defaults to '=' if not specified) and AMOUNT is any
    valid amount (e.g. '10000MB', '99 gb', '0.2T',
    'unlimited').

    If DESCRIPTION is not supplied then it will be the
    same as the NAME.

    If supplied then DEFAULT_FOR must be one of
    'registered' or 'unregistered', in which case the new
    quota will become the default for that class of user
    (overriding any default which was previously defined).

    Users and groups can also be associated with the new
    quota with the -u/--users and -g/--groups options.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Deal with quota specification
    operation,amount = handle_quota_spec(quota)
    # Deal with description
    if description is None:
        description = name
    # Deal with user and groups
    if users:
        users = users.split(',')
    if groups:
        groups = groups.split(',')
    # Create new quota
    sys.exit(create_quota(gi,name,description,
                          amount,operation,
                          default=default_for,
                          users=users,
                          groups=groups))

@nebulizer.command(name="quota_mod")
@click.option('-n','--name',metavar="NEW_NAME",
              help="new name for the quota.")
@click.option('-d','--description',metavar="NEW_DESCRIPTION",
              help="new description for the quota.")
@click.option('-q','--quota-size',metavar="NEW_QUOTA_SIZE",
              help="new quota size in the form "
              "'[OPERATION][AMOUNT]' (e.g. '=0.2T').")
@click.option('--default_for',metavar="registered|unregistered",
              help="set the quota as the default for either "
              "'registered' or 'unregistered' users.")
@click.option('-a','--add-users',metavar="EMAIL[,EMAIL...]",
              help="list of user emails to associate with the "
              "quota, separated by commas.")
@click.option('-r','--remove-users',metavar="EMAIL[,EMAIL...]",
              help="list of user emails to disassociate from "
              "the quota, separated by commas.")
@click.option('-A','--add-groups',metavar="GROUP[,GROUP...]",
              help="list of group names to associate with the "
              "quota, separated by commas.")
@click.option('-R','--remove-groups',metavar="GROUP[,GROUP...]",
              help="list of group names to disassociate from "
              "the quota, separated by commas.")
@click.option('-u','--undelete',is_flag=True,
              help="restores a previously deleted quota")
@click.argument("galaxy")
@click.argument("quota")
@pass_context
def quota_mod(context,galaxy,quota,name=None,description=None,
              quota_size=None,default_for=None,add_users=None,
              remove_users=None,add_groups=None,remove_groups=None,
              undelete=False):
    """
    Modify an existing quota.

    Updates the definition of the existing QUOTA in GALAXY.

    The command line arguments can be used to modify any of
    the quota's attributes, to set a new name, description
    or quota size and type.

    Users and groups can also be associated with or
    disassociated from the quota, and deleted quotas can
    be restored and modified.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Deal with quota specification
    if quota_size:
        operation,amount = handle_quota_spec(quota_size)
    else:
        operation = None
        amount = None
    # Deal with user and groups
    if add_users:
        add_users = add_users.split(',')
    if remove_users:
        remove_users = remove_users.split(',')
    if add_groups:
        add_groups = add_groups.split(',')
    if remove_groups:
        remove_groups = remove_groups.split(',')
    # Create new quota
    sys.exit(update_quota(gi,quota,
                          new_name=name,
                          new_description=description,
                          new_amount=amount,
                          new_operation=operation,
                          new_default=default_for,
                          add_users=add_users,
                          remove_users=remove_users,
                          add_groups=add_groups,
                          remove_groups=remove_groups,
                          undelete=undelete))

@nebulizer.command(name="quota_del")
@click.argument("galaxy")
@click.argument("quota")
@click.option('-y','--yes',is_flag=True,
              help="don't ask for confirmation of deletions.")
@pass_context
def quota_del(context,galaxy,quota,yes):
    """
    Delete quota.

    Deletes QUOTA from GALAXY.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Delete quota
    sys.exit(delete_quota(gi,quota,no_confirm=yes))

@nebulizer.command(name="config")
@click.argument("galaxy")
@click.option('--name',
              help="only show configuration items that match "
              "NAME. Can include glob-style wild-cards.")
@pass_context
def config(context,galaxy,name=None):
    """
    Report the Galaxy configuration.

    Reports the available configuration information from
    GALAXY. Use --name to filter which items are reported.
    """
    # Get a Galaxy instance
    gi = context.galaxy_instance(galaxy,validate_key=False)
    if gi is None:
        logger.critical("Failed to connect to Galaxy instance")
        sys.exit(1)
    # Fetch and report configuration
    config = get_galaxy_config(gi)
    items = sorted(config.keys())
    if name:
        name = name.lower()
        items = [item for item in items if fnmatch.fnmatch(item.lower(),
                                                           name)]
    output = Reporter()
    for item in items:
        output.append((item,config[item]))
    output.report(rstrip=True)

@nebulizer.command(name="ping")
@click.option('-c','--count',metavar='COUNT',default=0,
              help="if set then stop after sending COUNT requests "
              "(default is to send requests forever).")
@click.option('-i','--interval',metavar='INTERVAL',default=5,
              help="set the interval between sending requests in "
              "seconds (default is 5 seconds).")
@click.option('-t','--timeout',metavar='LIMIT',default=0,
              help="specify timeout limit in seconds when no "
              "connection can be made.")
@click.argument("galaxy")
@pass_context
def ping(context,galaxy,count,interval=5,timeout=None):
    """
    'Ping' a Galaxy instance.

    Sends a request to GALAXY and reports the status of the
    response and the time taken.
    """
    try:
        galaxy_url,_ = Credentials().fetch_key(galaxy)
    except KeyError:
        galaxy_url = galaxy
    click.echo("PING %s" % galaxy_url)
    nrequests = 0
    timeout_timer = 0
    while True:
        try:
            # Get a Galaxy instance
            gi = context.galaxy_instance(galaxy_url,validate_key=False)
            if gi is None:
                click.echo("%s: failed to connect" % galaxy_url)
                status_code = 1
            else:
                status_code,response_time = ping_galaxy_instance(gi)
                if status_code != 0:
                    msg = "failed (error code %s)" % status[0]
                else:
                    msg = "ok"
                click.echo("%s: status = %s time = %.3f (ms)" %
                           (galaxy_url,msg,response_time*1000.0))
            # Deal with count limit, if set
            if count != 0:
                nrequests += 1
                if nrequests >= count:
                    break
            # Check for timeout
            if timeout and timeout_timer > timeout:
                click.echo("Timeout limit reached without "
                           "connecting")
                break
            # Wait before sending next request
            time.sleep(interval)
            # Update timer for failed connection
            if status_code != 0:
                timeout_timer += interval
            else:
                timeout_timer = 0
        except KeyboardInterrupt:
            break
        except Exception as ex:
            click.echo("Uncaught exception: %s" % ex)
            status_code = 1
            break
    sys.exit(status_code)

@nebulizer.command(name="whoami")
@click.argument("galaxy")
@pass_context
def whoami(context,galaxy,):
    """
    Print user details associated with API key.
    """
    logger.debug("Debugging mode")
    # Get a Galaxy instance
    try:
        gi = context.galaxy_instance(galaxy)
    except Exception as ex:
        logger.warning(ex)
        gi = None
    if gi is None:
        logger.fatal("Failed to connect to Galaxy instance")
        sys.exit(1)
    user = get_current_user(gi)
    if user is None:
        logger.warning("No associated user for this API key")
    else:
        click.echo("%s" % user['email'])
