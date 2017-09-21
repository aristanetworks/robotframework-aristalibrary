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

import XXX


class AristaExpect(object):
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'

    def __init__(self, cmd):
        self.cmd = cmd
        self.arista_lib = BuiltIn().get_library_instance('AristaLibrary')
        self.result = {}

    # ---------------- Start Core Keywords ---------------- #

    def initialize_tests_on_switch(self, switch_index=None):
        # Convert the passed in switch_id to the actual switch index
        # to be used as a key for storing the results

        if (switch_index):
            switch_list = [self.arista_lib.get_switch(switch_index)]
        else:
            switch_list = self.arista_lib.get_switches()

        for switch in switch_list:
            index = switch['index']
            self.arista_lib.change_to_switch(index)

            if re.match(r'^show running-config all', self.cmd):
                # If command is show running-config all, get the running
                # config from the AristaLibrary object
                reply = self.arista_lib.get_running_config()
                self.result[index] = reply.split('\n')
            else:
                # Command is user specified, run it on the switch
                reply = self.arista_lib.enable(self.cmd)
                self.result[index] = reply[0]['result']

        XXX.file('initialize_tests_on_switch', self.result)

        return self.result

    def expect(self, key, match_type, value):
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
        getattr(self, match_string)(keylist, returned, value)

    # ---------------- Keyword 'is' and its equivalents ---------------- #

    def _is(self, key, returned, value):
        if returned != value:
            raise RuntimeError(
                'Key: \'{}\', Found: \'{}\', Expected: \'{}\''
                .format(key, returned, value)
            )

    def _is_equal_to(self, key, returned, value):
        return self._is(key, returned, value)

    def _isequalto(self, key, returned, value):
        return self._is(key, returned, value)

    def _equals(self, key, returned, value):
        return self._is(key, returned, value)

    def _to_be(self, key, returned, value):
        return self._is(key, returned, value)

    def _tobe(self, key, returned, value):
        return self._is(key, returned, value)

    # ---------------- Keyword 'is not' and its equivalents ---------------- #

    def _is_not(self, key, returned, value):
        if returned == value:
            raise RuntimeError(
                'Key: \'{}\', Found: \'{}\', Expected to not be: \'{}\''
                .format(key, returned, value)
            )

    def _isnot(self, key, returned, value):
        return self._is_not(key, returned, value)

    def _is_not_equal_to(self, key, returned, value):
        return self._is_not(key, returned, value)

    def _isnotequalto(self, key, returned, value):
        return self._is_not(key, returned, value)

    def _to_not_be(self, key, returned, value):
        return self._is_not(key, returned, value)

    def _tonotbe(self, key, returned, value):
        return self._is_not(key, returned, value)

    # ---------------- Keyword 'starts with' and equivalents ---------------- #

    def _starts_with(self, key, returned, value):
        if not returned.startswith(value):
            raise RuntimeError(
                'Key: \'{}\', Found: \'{}\', Expected to start with: \'{}\''
                .format(key, returned, value)
            )

    def _startswith(self, key, returned, value):
        return self._starts_with(key, returned, value)

    def _begins_with(self, key, returned, value):
        return self._starts_with(key, returned, value)

    def _beginswith(self, key, returned, value):
        return self._starts_with(key, returned, value)

    # ---------------- Keyword 'contains' and equivalents ---------------- #

    def _contains(self, key, returned, value):
        if isinstance(returned, str) or isinstance(returned, unicode):
            if value not in returned:
                raise RuntimeError(
                    'Key: \'{}\', Found: \'{}\', Expected to contain: \'{}\''
                    .format(key, returned, value)
                )
        elif isinstance(returned, list):
            if value not in returned:
                raise RuntimeError(
                    'Did not find \'{}\' in \'{}\''.format(value, key)
                )
        else:
            raise RuntimeError('Unable to determine type of return value')

    def _to_contain(self, key, returned, value):
        return self._contains(key, returned, value)

    # ------------- Keyword 'does not contain' and equivalents ------------- #

    def _does_not_contain(self, key, returned, value):
        if isinstance(returned, str) or isinstance(returned, unicode):
            if value in returned:
                raise RuntimeError(
                        'Key: \'{}\', Found: \'{}\''
                        ', Expected to not contain: \'{}\''
                        .format(key, returned, value)
                        )
        elif isinstance(returned, list):
            if value in returned:
                raise RuntimeError(
                        'Found \'{}\' in \'{}\''.format(value, key)
                        )
        else:
            raise RuntimeError('Unable to determine type of return value')

    def _to_not_contain(self, key, returned, value):
        return self._does_not_contain(key, returned, value)


class AristaExpectConfig(AristaExpect):
    # This is a wrapper class for using the AristaExpect functionality
    # against the runninc-config of the switch. No command is passed to
    # the Library import in Robot Framework. The wrapper sets the command
    # to 'show running-config all' and the key passed to the Expect function
    # should be 'config', e.g. 'Expect  config  to contain  <config string>'.
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'

    def __init__(self):
        AristaExpect.__init__(self, 'show running-config all')
