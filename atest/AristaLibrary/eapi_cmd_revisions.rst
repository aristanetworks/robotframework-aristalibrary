========================================
Sample Test Example in RST documentation
========================================

.. raw:: html

   <!-- This class allows us to hide the test setup part -->
   <style type="text/css">.hidden { display: none; }</style>

.. contents::
    :local:

This example demonstrates how RobotFramework tests can be embedded in
ReStructuredText documentation.  If you are converting an existing
tab-separated test suite, convert tabs to 4-spaces within the RST file.

The testcases should be in `code:: robotframework` blocks.

Installing RobotFramework
=========================

To execute this test, setup the following::

    pip install robotframework docutils Pygments
    git clone https://github.com/arista-eosplus/robotframework-aristalibrary.git
    cd robotframework-aristalibrary/
    python setup.py install


Executing tests
===============

Start tests using one of the examples, below::

    robot demo/sample_test_refactored.rst

    robot --variable SW1_HOST:localhost --variable SW1_PORT:61080 \
          --variable USERNAME:eapiuser --variable PASSWORD:icanttellyou \
          demo/sample_test_refactored.rst

    robot --variablefile demo/myvariables.py
          demo/sample_test_refactored.rst

Variable files
--------------

Variable files are just python modules with KEY = value pairs.

Example `myvariables.py`::

    """ My custom values for this test suite
    """

    SW1_HOST = 'localhost'
    SW1_PORT = 61080
    USERNAME = 'eapiuser'
    PASSWORD = 'icanttellyou'

Suite Setup
===========

.. code:: robotframework
   :class: hidden

    *** Settings ***
    Documentation    This is a sample Robot Framework suite which takes advantage of
    ...    the AristaLibrary for communicating with and controlling Arista switches.
    ...    Run with:
    ...    pybot --pythonpath=AristaLibrary --noncritical new demo/sample-test-refactored.txt

    Library    AristaLibrary
    Library    AristaLibrary.Expect
    Library    Collections
    Suite Setup    Connect To Switches
    Suite Teardown    Clear All Connections

    *** Variables ***
    ${TRANSPORT}    http
    ${SW1_HOST}    localhost
    ${SW1_PORT}    2080
    ${SW2_HOST}    localhost
    ${SW2_PORT}    2081
    ${USERNAME}    vagrant
    ${PASSWORD}    vagrant

    *** Keywords ***
    Connect To Switches
        [Documentation]    Establish connection to a switch which gets used by test cases.
        Connect To    host=${SW1_HOST}    transport=${TRANSPORT}    username=${USERNAME}    password=${PASSWORD}    port=${SW1_PORT}
        Configure    hostname veos0
        #Connect To    host=${SW2_HOST}    transport=${TRANSPORT}    username=${USERNAME}    password=${PASSWORD}    port=${SW2_PORT}
        #Configure    hostname veos1

Test Cases
===============

.. code:: robotframework

    *** Test Cases ***
    eAPI Command Revision
        [tags]    Production

        # Default revision
        ${output}=    Enable    show cvx
        ${result}=    Get From Dictionary    ${output[0]}    result
        Log    ${result}
        Dictionary Should Not Contain Key  ${result}  clusterMode

        # Specify revision 2 for this command
        ${show_cvx}=  Create Dictionary  cmd=show cvx  revision=${2}
        ${cmds}=  Create List  ${show_cvx}
        Log List  ${cmds}
        ${output}=    Enable    ${cmds}
        ${result}=    Get From Dictionary    ${output[0]}    result
        Log    ${result}
        Dictionary Should Contain Key  ${result}  clusterMode

    eAPI Command Revision with Expect
        [tags]    Production

        # Specify revision 2 for this command
        ${show_cvx}=  Create Dictionary  cmd=show cvx  revision=${2}
        ${cmds}=  Create List  ${show_cvx}
        Log List  ${cmds}
        Get Command Output  cmd=${cmds}
        Expect  clusterMode  is  False

There you go...  Tests, embedded within documentation!
