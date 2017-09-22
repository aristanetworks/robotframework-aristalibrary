# Copyright (c) 2017, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import re

from robot.libraries.BuiltIn import BuiltIn

AE_ERR = 'AristaExpect: '    # AristaExpect Error prefix


class AristaExpect(object):
    """AristaExpect - A Robot Framework library for testing Arista EOS
    devices using an Expect keyword.

    This library contains two formats for using the Expect keyword for
    testing Arista EOS devices. The first format is for testing the output
    of single EOS command, such as a `show` command. The second method
    is for testing the output of the EOS `show running-config all` command,
    and is useful for checking configurations that do not have a built-in
    command to retrieve settings, such as whether ip routing is enabled or
    disabled.

    Test setup is a two-step process: 1) import the AristaExpect library, and
    2) initialize the library (which retrieves the output of the specified
    EOS command). Initialization may be repeated, and may specify alternate
    commands if desired.

    After the test library has been initialized, individual test cases
    may be run using the Expect keyword. See the documentation for the
    Expect keyword for additional details.

    Examples:

        Use the AristaExpect library to validate the results of 'show
        interfaces ethernet 1':

            # This example assigns the 'show interfaces ethernet 1' command
            # at the time of library import.

            *** Settings ***
            # Import the prerequisite AristaLibrary first
            | Library | AristaLibrary |
            # Import the AristaExpect library for the command
            # show interfaces ethernet 1':
            | Library | AristaExpect | show interfaces ethernet 1 |

            *** Test Cases ***
            Initialize the testbed
                | Initialize Tests On Switch |

            Verify autoNegotiate is unknown
                | Expect | interfaces Ethernet1 autoNegotiate | is | unknown |

            Verify interfaceStatus is not disconnected
                | Expect | interfaces Ethernet1 interfaceStatus | is not | disconnected |

        Use the AristaExpect library to validate the results of 'show
        interfaces ethernet 2':

            # This example assigns the 'show interfaces ethernet 1' command
            # when the testbed is initialized

            *** Settings ***
            # Import the prerequisite AristaLibrary first
            | Library | AristaLibrary |
            # Import the AristaExpect library without a command specification
            | Library | AristaExpect |

            *** Test Cases ***
            Initialize the testbed for the command 'show interfaces ethernet 1'
                | Initialize Tests On Switch | cmd=show interfaces ethernet 1 |

            Verify autoNegotiate is unknown
                | Expect | interfaces Ethernet1 autoNegotiate | is | unknown |

            Verify interfaceStatus is not disconnected
                | Expect | interfaces Ethernet1 interfaceStatus | is not | disconnected |

        Use the AristaExpect library to validate hostnames before and
        after changing the hostname:

            # This example combines multiple initialization calls to
            # validate changes in the current config. The initialization
            # calls here do not update the 'show hostname' command that
            # is defined in the library import call.

            *** Settings ***
            # Import the prerequisite AristaLibrary first
            | Library | AristaLibrary |
            # Import the AristaExpect library for the command 'show hostname'
            | Library | AristaExpect | show hostname |

            *** Test Cases ***
            Initialize the testbed for the command 'show hostname'
                | Initialize Tests On Switches |
                | Expect | hostname | to be | first-hostname |
                # Send an AristaLibrary command to change the hostname
                | Configure | hostname new-hostname |
                | Reinitialize Tests On Switch | 2 |
                | Expect | hostname | to be | new-hostname |

        Use the AristaExpect library to validate different command results:

            # This example has two initialization calls that each give
            # a different command, with the Expect keyword to validate
            # the results of the commands.

            *** Settings ***
            # Import the prerequisite AristaLibrary first
            | Library | AristaLibrary |
            # Import the AristaExpect library without a command specification
            | Library | AristaExpect |

            *** Test Cases ***
            Validate the output of 'show hostname'
                | Change To Switch | 1 |
                | Initialize Tests On Switch | cmd=show hostname |
                | Expect | hostname | to be | first-hostname |

            Validate the output of 'show interfaces ethernet 1'
                | Change To Switch | 1 |
                | Initialize Tests On Switch | cmd=show interfaces ethernet 1 |
                | Expect | interfaces Ethernet1 autoNegotiate | is | unknown |
                | Expect | interfaces Ethernet1 interfaceStatus | is not | disconnected |

        Use the AristaExpect library to validate lines in the running-config:

            *** Settings ***
            # Import the prerequisite AristaLibrary first
            | Library | AristaLibrary |
            # Import the AristaExpect library to validate the running-config:
            | Library | AristaExpect.AristaExpectConfig |

            *** Test Cases ***
            Initialize the testbed
                | Initialize Tests On Switch |

            # NOTE that for AristaExpectConfig test cases, the identifier
            # key is always 'config'.

            Verify the running-config contains the line 'ip routing'
                | Expect | config | to contain | ip routing |

            Verify the running-config does not contain the line 'no ip multicast-routing'
                | Expect | config | to not contain | no ip multicast-routing |

        NOTE: The AristaExpect library relies on the AristaLibrary for
        connection management. The AristaLibrary *must* be imported before
        the AristaExpect library to ensure proper access to the connection
        management routines.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'

    def __init__(self, cmd=None):
        # Store the command passed in when the library is imported
        self.import_cmd = cmd
        # Get the AristaLibrary instance in use so we can reference
        # the list of connections
        self.arista_lib = BuiltIn().get_library_instance('AristaLibrary')
        # Initialize the switch_cmd and result dictionaries as empty
        self.switch_cmd = {}
        self.result = {}

    # ---------------- Start Core Keywords ---------------- #

    def initialize_tests_on_switch(self, switch_id=None, cmd=None):
        """This keyword initializes the testbed by executing the desired
        EOS command on each switch connection established in the AristaLibrary
        instance associated with the test suite being executed. The result
        of running the command on each switch is stored in an indexed member
        of the AristaExpect object, where the index is the index number of
        the connection that is established in the AristaLibrary object.

        Args:
            switch_id (int, optional): The index id for a specific switch
                connection defined in the AristaLibrary. If not specified,
                all available switch connections will be initialized.
            cmd (string): The command string that will be exectuted
                on the switch or switches determined by switch_id. If not
                specified, the previous command sent to each switch will
                be reused, or the command used in the library import if
                no previous command has been sent. Default is None.

        NOTE: The result of the command is not accessible to the test cases
        within a test suite that imports the AristaExpect library. All tests
        must be processed using an AristaExpect-style keyword.
        """
        # Convert the passed in switch_id to the actual switch indexes
        # to be used as keys for storing the results. Use all switches
        # if switch_id is not specified.
        if switch_id:
            switch_list = [self.arista_lib.get_switch(switch_id)]
        else:
            switch_list = self.arista_lib.get_switches()

        for switch in switch_list:
            index = switch['index']
            run_cmd = None
            # Determine what command is to be executed.
            # Command priority:
            #   1. cmd parameter passed to this method
            #   2. last used command on this switch (switch_cmds)
            #   3. cmd parameter passed to the library import (import_cmd)
            #   4. None - result value with remain unset
            if cmd:
                # set run_cmd and switch_cmd for this index to cmd parameter
                run_cmd = self.switch_cmd[index] = cmd
            elif index in self.switch_cmd and self.switch_cmd[index]:
                # value is already stored, just set run_cmd
                run_cmd = self.switch_cmd[index]
            elif self.import_cmd:
                # set run_cmd and switch_cmd for this index to import_cmd
                run_cmd = self.switch_cmd[index] = self.import_cmd
            else:
                # set run_cmd and switch_cmd for this index to None
                run_cmd = self.switch_cmd[index] = None

            # Clear any existing result
            self.result[index] = None

            self.arista_lib.change_to_switch(index)

            if self.import_cmd and re.match(r'^show running-config all', self.import_cmd):
                # If command is show running-config all, get the running
                # config from the AristaLibrary object
                reply = self.arista_lib.get_running_config()
                self.result[index] = reply.split('\n')
            elif run_cmd:
                # Command is user specified, run it on the switch
                reply = self.arista_lib.enable(run_cmd)
                self.result[index] = reply[0]['result']

        return self.result

    def initialize_tests_on_switches(self, cmd=None):
        """This keyword initializes the testbed on all switch connections
        by sending the defined command to each switch. This is simply an
        alias to initialize_tests_on_switch without the switch_id parameter.

        Args:
            cmd (string): The command string that will be exectuted
                on the all the switches configured by the AristaLibrary.
                If not specified, the previous command sent to each
                switch will be reused, or the command used in the library
                import if no previous command has been sent. Default is None.
        """
        return self.initialize_tests_on_switch(cmd=cmd)

    def reinitialize_tests_on_switch(self, switch_id=None, cmd=None):
        """Alias keyword for initialize_tests_on_switch
        """
        return self.initialize_tests_on_switch(switch_id=switch_id, cmd=cmd)

    def reinitialize_tests_on_switches(self, cmd=None):
        """Alias keyword for initialize_tests_on_switches
        """
        return self.initialize_tests_on_switches(cmd=cmd)

    def expect(self, key, match_type, match_value):
        """This keyword provides a method of testing various types of values
        within the command output stored after running the 'Initialize Tests
        On Switch' keyword has been run.

        Args:
            key (string): The key within the result that will be compared. This
                is usually a json object key string that points to a specific
                part of the result.

                To indicate depth in the result json object, separate subkeys
                with a single space. So result['key1']['sub1']['sub2'] will
                be the string 'key1 sub1 sub2'.

                When testing against the running-config, the key
                must be 'config'.

            match_type (string): The match type string to be used for
                comparison of the result value and the expected value. See
                the examples and documentation below for available match
                type keywords. A passing test is one in which comparing the
                result[key] against the 'value' parameter evaluates to True.

            match_value (string): The value against which the 'key' value
                will be compared using the 'match_type' string.

        Examples:
            # result['interfaces']['ethernet1']['description'] should be
            # exactly 'MyEth1'
            | Expect | interface ethernet1 description | to be | MyEth1 |

            # result['interfaces']['ethernet1']['duplex'] should begin
            # with the string 'duplex'
            | Expect | interface ethernet1 duplex | starts with | duplex |

            # running-config should contain the exact line 'ip routing'
            | Expect | config | to contain line | ip routing |
            # meaning the running-config should not contain 'no ip routing'
            # and the following keyword example will fail
            | Expect | config | to contain line | no ip routing |

        Match Type:
            The match type string can be a common comparison phrase to
            indicate how the key in the command result should be compared
            against the expected value. Often there are multiple ways to
            specify the same type of comparison. The AristaExpect library
            is designed to recognize these variations. However, not all
            possible variations and match phrases have been implemented.
            A phrase or variation that does not match a known implementaion
            will generate a test failure with a ValueError stating the
            match type is currently unimplemented.

            Example match types would be
                is:
                    equivalents: is equal to, isequalto, equals, to be, tobe
                    match description: exact match
                    examples:
                        | Expect | name | is | name | => PASS
                        | Expect | name | is equal to | namex | => FAIL

                is not:
                    equivalents: isnot, is not equal to, isnotequalto,
                        to not be, tonotbe,
                    match description: not an exact match
                    examples:
                        | Expect | name | is not | eman | => PASS
                        | Expect | name | is not equal to | name | => FAIL

                starts with:
                    equivalents: startswith, begins with, beginswith
                    match description: result string begins with value
                    examples:
                        | Expect | name | beginswith | na | => PASS
                        | Expect | name | starts with | e | => FAIL

                contains:
                    equivalents: to contain, tocontain
                    match description: result string contains value string
                    examples:
                        | Expect | name | contains | am | => PASS
                        | Expect | name | to contain | xam | => FAIL

                does not contain:
                    equivalents: doesnotcontain, to not contain, tonotcontain
                    match description: result string should not contain value string
                    examples:
                        | Expect | name | does not contain | xyz | => PASS
                        | Expect | name | to not contain | am | => FAIL

                contains line:
                    equivalents: containsline, to contain line, tocontainline
                    match description: result string or list contains value
                        string as a complete line
                    examples:
                        | Expect | config | contains line | ip routing | => PASS
                        | Expect | config | to contain line | not a config line | => FAIL

                does not contain line:
                    equivalents: doesnotcontainline, to not contain line,
                        tonotcontainline
                    match description: result string or list does not contain
                        value string as a complete line
                    examples:
                        | Expect | config | does not contain line | not a real line | => PASS
                        | Expect | config | to not contain line | ip routing | => FAIL

        """
        index = self.arista_lib.get_switch()['index']
        match_string = '_{}'.format(match_type.replace(' ', '_').lower())
        returned = self.result[index]
        keylist = key.split()
        if key != 'config':
            for k in keylist:
                returned = returned[k]

        # Call the method referenced by the match_string, passing in
        # the values of the keylist, the returned value found by the
        # keylist, and the expected value to be used for matching
        try:
            getattr(self, match_string)(keylist, returned, match_value)
        except AttributeError:
            # AttributeError is misleading in this case, since the problem
            # is that the match_string has not been implemented. Instead,
            # return a ValueError explaining that the match type is not
            # implemented.
            raise ValueError(
                '{}"{}" is currently not implemented for Expect'
                .format(AE_ERR, match_type)
            )

    # ---------------- Keyword 'is' and its equivalents ---------------- #

    def _is(self, key, returned, match):
        # Fail if the returned value does not equal the match value
        if returned != match:
            raise RuntimeError(
                '{}Key: \'{}\', Found: \'{}\', Expected: \'{}\''
                .format(AE_ERR, key, returned, match)
            )

    def _is_equal_to(self, key, returned, match):
        return self._is(key, returned, match)

    def _isequalto(self, key, returned, match):
        return self._is(key, returned, match)

    def _equals(self, key, returned, match):
        return self._is(key, returned, match)

    def _to_be(self, key, returned, match):
        return self._is(key, returned, match)

    def _tobe(self, key, returned, match):
        return self._is(key, returned, match)

    # ---------------- Keyword 'is not' and its equivalents ---------------- #

    def _is_not(self, key, returned, match):
        # Fail if the returned value does equals the match value
        if returned == match:
            raise RuntimeError(
                '{}Key: \'{}\', Found: \'{}\', Expected to not be: \'{}\''
                .format(AE_ERR, key, returned, match)
            )

    def _isnot(self, key, returned, match):
        return self._is_not(key, returned, match)

    def _is_not_equal_to(self, key, returned, match):
        return self._is_not(key, returned, match)

    def _isnotequalto(self, key, returned, match):
        return self._is_not(key, returned, match)

    def _to_not_be(self, key, returned, match):
        return self._is_not(key, returned, match)

    def _tonotbe(self, key, returned, match):
        return self._is_not(key, returned, match)

    # ---------------- Keyword 'starts with' and equivalents ---------------- #

    def _starts_with(self, key, returned, match):
        # Fail if the returned value does not start with the match value
        if not returned.startswith(match):
            raise RuntimeError(
                '{}Key: \'{}\', Found: \'{}\', Expected to start with: \'{}\''
                .format(AE_ERR, key, returned, match)
            )

    def _startswith(self, key, returned, match):
        return self._starts_with(key, returned, match)

    def _begins_with(self, key, returned, match):
        return self._starts_with(key, returned, match)

    def _beginswith(self, key, returned, match):
        return self._starts_with(key, returned, match)

    # ---------------- Keyword 'contains' and equivalents ---------------- #

    def _contains(self, key, returned, match):
        if isinstance(returned, str) or isinstance(returned, unicode):
            # If we have a (unicode) string, fail if the returned value
            # does not contain the match value
            if match not in returned:
                raise RuntimeError(
                    '{}Key: \'{}\', Found: \'{}\', Expected to contain: \'{}\''
                    .format(AE_ERR, key, returned, match)
                )
        elif isinstance(returned, list):
            # If we have a list, fail if the match value is not in the list
            if match not in returned:
                raise RuntimeError(
                    '{}Did not find \'{}\' in \'{}\''.format(AE_ERR, match, key)
                )
        else:
            # Not sure what type of return value we have
            raise RuntimeError(
                '{}Unable to determine type of return value'
                .format(AE_ERR)
            )

    def _to_contain(self, key, returned, match):
        return self._contains(key, returned, match)

    def _tocontain(self, key, returned, match):
        return self._contains(key, returned, match)

    # ---------------- Keyword 'does not contain' and equivalents ------------ #

    def _does_not_contain(self, key, returned, match):
        if isinstance(returned, str) or isinstance(returned, unicode):
            # If we have a (unicode) string, fail if the returned value
            # contains the match value as a substring
            if match in returned:
                raise RuntimeError(
                    '{}Key: \'{}\', Found: \'{}\', '
                    'Expected to not contain: \'{}\''
                    .format(AE_ERR, key, returned, match)
                )
        elif isinstance(returned, list):
            # If we have a list, fail if the match value is in the list
            if match in returned:
                raise RuntimeError(
                    '{}Found \'{}\' in \'{}\''.format(AE_ERR, match, key)
                )
        else:
            # Not sure what type of return value we have
            raise RuntimeError(
                '{}Unable to determine type of return value'.format(AE_ERR)
            )

    def _doesnotcontain(self, key, returned, match):
        return self._does_not_contain(key, returned, match)

    def _to_not_contain(self, key, returned, match):
        return self._does_not_contain(key, returned, match)

    def _tonotcontain(self, key, returned, match):
        return self._does_not_contain(key, returned, match)

    # ---------------- Keyword 'contains line' and equivalents ---------------- #

    def _contains_line(self, key, returned, match):
        if isinstance(returned, str) or isinstance(returned, unicode):
            # If we have a (unicode) string, fail if the returned value
            # does not equal the match value
            if returned != match:
                raise RuntimeError(
                    '{}Key: \'{}\', Found: \'{}\', Expected to be: \'{}\''
                    .format(AE_ERR, key, returned, match)
                )
        elif isinstance(returned, list):
            # If we have a list, fail if the match value is not in the list
            if match not in returned:
                raise RuntimeError(
                    '{}Did not find \'{}\' in \'{}\''.format(AE_ERR, match, key)
                )
        else:
            # Not sure what type of return value we have
            raise RuntimeError(
                '{}Unable to determine type of return value'.format(AE_ERR)
            )

    def _contains_line(self, key, returned, match):
        return self._contains(key, returned, match)

    def _to_contain_line(self, key, returned, match):
        return self._contains(key, returned, match)

    def _tocontainline(self, key, returned, match):
        return self._contains(key, returned, match)

    # ---------------- Keyword 'does not contain line' and equivalents ------- #

    def _does_not_contain_line(self, key, returned, match):
        if isinstance(returned, str) or isinstance(returned, unicode):
            # If we have a (unicode) string, fail if the returned value
            # equals the match value
            if returned == match:
                raise RuntimeError(
                    '{}Found \'{}\' in key \'{}\', Expected to not be found'
                    .format(AE_ERR, match, key)
                )
        elif isinstance(returned, list):
            # If we have a list, fail if the list contains the match value
            if match in returned:
                raise RuntimeError(
                    '{}Found \'{}\' in \'{}\''.format(AE_ERR, match, key)
                )
        else:
            # Not sure what type of return value we have
            raise RuntimeError(
                '{}Unable to determine type of return value'.format(AE_ERR)
            )

    def _doesnotcontainline(self, key, returned, match):
        return self._does_not_contain_line(key, returned, match)

    def _to_not_contain_line(self, key, returned, match):
        return self._does_not_contain_line(key, returned, match)

    def _tonotcontainline(self, key, returned, match):
        return self._does_not_contain_line(key, returned, match)


class AristaExpectConfig(AristaExpect):
    # This is a wrapper class for using the AristaExpect functionality
    # against the runninc-config of the switch. No command is passed to
    # the Library import in Robot Framework. The wrapper sets the command
    # to 'show running-config all' and the key passed to the Expect function
    # should be 'config', e.g. 'Expect  config  to contain  <config string>'.
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'

    def __init__(self):
        AristaExpect.__init__(self, 'show running-config all')
