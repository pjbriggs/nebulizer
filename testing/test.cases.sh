#!/bin/bash
#
# Functions implementing test cases for nebulizer
#
# Ping Galaxy
function ping_galaxy() {
    nebulizer $NEBULIZER_OPTS ping -c 1 $GALAXY
    return $?
}
#
# List users
function list_users() {
    nebulizer $NEBULIZER_OPTS list_users $GALAXY
    return $?
}
#
# Add user
function create_user() {
    nebulizer $NEBULIZER_OPTS create_user $GALAXY -p $(pwgen 8 1) a.user@example.com
    return $?
}
#
# List installed tools
function list_installed_tools() {
    nebulizer $NEBULIZER_OPTS list_installed_tools $GALAXY
    return $?
}
#
# Install a tool
function install_tool() {
    nebulizer $NEBULIZER_OPTS install_tool --timeout 20 $GALAXY toolshed.g2.bx.psu.edu pjbriggs trimmomatic 6eeacf19a38e
    return $?
}
#
# Update a tool
function update_tool() {
    nebulizer $NEBULIZER_OPTS update_tool --timeout 20 $GALAXY toolshed.g2.bx.psu.edu pjbriggs trimmomatic
    return $?
}
