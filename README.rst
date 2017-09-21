The Arista Library for Robot Framework
======================================

Introduction
------------

AristaLibrary aims to simplify testing projects on `Arista EOS <http://www.arista.com>`
using `Robot Framework <http://robotframework.org/>` by adding a number of
EOS-centric keywords. The Library works by using the PyEAPI module to
interact with EOS nodes.

Prerequisites
-------------

* `Robot Framework <http://robotframework.org/>`
* `PyEAPI <https://pypi.python.org/pypi/pyeapi>` (`GitHub <https://github.com/arista-eosplus/pyeapi>`)
* `Arista EOS <http://www.arista.com>` 4.12 or later
* Python 2.7

Installation
------------

The easiest way to install is to use `pip <http://www.pip-installer.org/en/latest/>`::

    pip install robotframework-aristalibrary

Upgrade using::

    pip install --upgrade robotframework-aristalibrary

To install from source::

    git clone https://github.com/arista-eosplus/robotframework-aristalibrary.git
    cd robotframework-aristalibrary
    # Optionally, checkout the development branch"
    git checkout develop"
    python setup.py install

Keyword Documentation
---------------------

See the `AristaLibrary <http://arista-eosplus.github.io/robotframework-aristalibrary/AristaLibrary.html>` keyword documentation.

Example Robot Test
------------------

::

    # -*- coding: robot -*-
    # :setf robot
    # :set noexpandtab
    *** Settings ***
    Documentation   This is a sample Robot Framework suite which takes advantage of
    ... the AristaLibrary for communicating with and controlling Arista switches.
    ... Run with:
    ... pybot --pythonpath=AristaLibrary demo/sample-test-refactored.txt

    Library AristaLibrary
    Library Collections
    Suite Setup Connect To Switches
    Suite Teardown  Clear All Connections

    *** Variables ***
    ${TRANSPORT}    http
    ${SW1_HOST} localhost
    ${SW1_PORT} 2080
    ${SW2_HOST} localhost
    ${SW2_PORT} 2081
    ${USERNAME} apiuser
    ${PASSWORD} donttell

    *** Test Cases ***
    Ping Test
        [Documentation] Configure Et1 on both nodes and ping between them
        [tags]  Configure
        Configure IP Int    1   ethernet1   10.1.1.0/31
        Configure IP Int    2   ethernet1   10.1.1.1/31

        ${output}=  Enable  ping 10.1.1.0
        ${result}=  Get From Dictionary ${output[0]}    result
        Log ${result}
        ${match}    ${group1}=  Should Match Regexp ${result['messages'][0]}    (\\d+)% packet loss
        Should Be Equal As Integers ${group1}   0   msg="Packets lost percent not zero!!!"

    *** Keywords ***
    Connect To Switches
        [Documentation] Establish connection to a switch which gets used by test cases.
        Connect To  host=${SW1_HOST}    transport=${TRANSPORT}  username=${USERNAME}
        ... password=${PASSWORD}    port=${SW1_PORT}
        Configure   hostname veos0
        Connect To  host=${SW2_HOST}    transport=${TRANSPORT}  username=${USERNAME}
        ... password=${PASSWORD}    port=${SW2_PORT}
        Configure   hostname veos1

    Configure IP Int
        [Arguments] ${switch}   ${interface}    ${ip}
        Change To Switch    ${switch}
        @{cmds}=    Create List
        ... default interface ${interface}
        ... interface ${interface}
        ... no switchport
        ... ip address ${ip}
        ... no shutdown
        Configure   ${cmds}

Release Notes
-------------

Release notes are available in the GitHub `releases <https://github.com/arista-eosplus/robotframework-aristalibrary/releases>`.

Support and Contacts
--------------------

AristaLibrary is a community-supported project, maintained by Arista EOS+.  Contact  the maintainers at `eosplus-dev@arista.com`.

Contributing
------------

Contributing is encouraged via pull requests.   Please see `<CONTRIBUTING.rst>`_ for more information.

License
-------

All code within this repository is made available under the BSD3 license and via the `<LICENSE>`_ file.
