# The Arista Library for Robot Framework

## Introduction
The enclosed project aims to simplify testing when using Robot Framework by adding a number of
EOS-centric keywords. The Library works by using the PyEAPI module to connect to and read information 
from EOS nodes. 

## Prerequisites
* The [Robot Framework](http://robotframework.org/)
* [PyEAPI](https://github.com/arista-eosplus/pyeapi)

## Documentation

See the [AristaLibrary](http://arista-eosplus.github.io/robotframework-aristalibrary/AristaLibrary.html) keyword documentation.

## Example

"""
# -*- coding: robot -*-
# :setf robot
# :set noexpandtab
*** Settings ***
Documentation   This is a sample Robot Framework suite which takes advantage of
... the AristaLibrary for communicating with and controlling Arista switches.
... Run with:
... pybot --pythonpath=AristaLibrary --noncritical new demo/sample-test-refactored.txt

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
${USERNAME} vagrant
${PASSWORD} vagrant

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
    Connect To  host=${SW1_HOST}    transport=${TRANSPORT}  username=${USERNAME}    password=${PASSWORD}    port=${SW1_PORT}
    Configure   hostname veos0
    Connect To  host=${SW2_HOST}    transport=${TRANSPORT}  username=${USERNAME}    password=${PASSWORD}    port=${SW2_PORT}
    Configure   hostname veos1

Configure IP Int
    [Arguments] ${switch}   ${interface}    ${ip}
    Change To Switch    ${switch}
    Configure   default interface ${interface}
    @{cmds}=    Create List default interface ${interface}  interface ${interface}  no switchportip address ${ip}   no shutdown
    Configure   ${cmds}
"""
