#!/usr/bin/env python
#
# options: click definitions for shared options and arguments
import click

def install_tool_dependencies_option(default='yes'):
    return click.option('--install-tool-dependencies',
                        default=default,
                        type=click.Choice(['yes','no']),
                        help="install tool dependencies via the "
                        "toolshed, if any are defined (default "
                        "is '%s')" % default)

def install_repository_dependencies_option(default='yes'):
    return click.option('--install-repository-dependencies',
                        default=default,
                        type=click.Choice(['yes','no']),
                        help="install repository dependencies "
                        "via the toolshed, if any are defined "
                        "(default is '%s')" % default)

def install_resolver_dependencies_option(default='yes'):
    return click.option('--install-resolver-dependencies',
                        default=default,
                        type=click.Choice(['yes','no']),
                        help="install dependencies through a "
                        "resolver that supports installation "
                        "(e.g. conda) (default is '%s')" %
                        default)
