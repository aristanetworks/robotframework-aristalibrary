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

    Library    AristaLibrary.py
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

    Configure IP Int
        [Arguments]    ${switch}    ${interface}    ${ip}
        Change To Switch    ${switch}
        Configure    default interface ${interface}
        @{cmds}=    Create List    default interface ${interface}    interface ${interface}    no switchport    ip address ${ip}    no shutdown
        Configure    ${cmds}

Test Cases
===============

.. code:: robotframework

    *** Test Cases ***
    Ping Test
        [Documentation]    Configure Et1 on both nodes and ping between them
        [tags]    Configure
        Configure IP Int    1    ethernet1    10.1.1.0/31
        #Configure IP Int    2    ethernet1    10.1.1.1/31

        ${output}=    Enable    ping 10.1.1.0    text
        ${result}=    Get From Dictionary    ${output[0]}    result
        Log    ${result}
        ${match}    ${group1}=    Should Match Regexp    ${result['output']}    (\\d+)% packet loss
        Should Be Equal As Integers    ${group1}    0    msg="Packets lost percent not zero!!!"

There you go...  Tests, embedded within documentation!
