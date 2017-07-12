#!/bin/bash
#
# Functions providing simple unit-test style infrastructure
#
# Usage:
#
# Define test functions which return 0 on success and non-zero
# on test failure e.g.:
#
# def test_something() {
#    if [ ! -z "$it_worked" ] ; then
#       return 0
#    else
#       return 1
#    fi
# }
#
# To use:
#
# init_testing
# run_test test_something
# ...etc...
# finish_testing
#
# Initialise test framework
function init_testing() {
    N_TESTS=0
    N_PASSED=0
    N_FAILED=0
    TEST_LOGS=$(mktemp --tmpdir=$(pwd) --suffix=.test_logs)
    touch $TEST_LOGS
}
# Run a test function
function run_test() {
    local status
    local stdout_file=$(mktemp --tmpdir=$(pwd) --suffix=.${1}.stdout)
    local stderr_file=$(mktemp --tmpdir=$(pwd) --suffix=.${1}.stderr)
    echo -n "${1}: "
    $1 1>$stdout_file 2>$stderr_file
    status=$?
    N_TESTS=$((N_TESTS+1))
    if [ $status == 0 ] ; then
	echo OK
	N_PASSED=$((N_PASSED+1))
    else
	echo FAIL
	N_FAILED=$((N_FAILED+1))
	cat >>$TEST_LOGS <<EOF
================================
TEST: $1
================================
STDOUT:
EOF
	cat $stdout_file >>$TEST_LOGS
	cat >>$TEST_LOGS <<EOF
STDERR:
EOF
	cat $stderr_file >>$TEST_LOGS
    fi
    /bin/rm -f $stdout_file
    /bin/rm -f $stderr_file
}
# Report the test results
function finish_testing() {
    local exit_code=0
    if [ $N_FAILED -gt 0 ] ; then
	exit_code=1
	cat $TEST_LOGS
    fi
    /bin/rm -f $TEST_LOGS
    echo "Ran $N_TESTS tests: $N_PASSED passed, $N_FAILED failed"
    return $exit_code
}
