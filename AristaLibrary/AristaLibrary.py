# Copyright (c) 2015, Arista Networks, Inc.
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
#

import pyeapi
from pyeapi.eapilib import CommandError
from pyeapi.utils import make_iterable
from robot.api import logger
from robot.utils import ConnectionCache
import re


class AristaLibrary:
    """AristaLibrary - A Robot Framework Library for testing Arista EOS Devices.

    The AristaLibrary has been designed to simplify the task of configuration
    validation and verification. If you are familiar with Command-API(eAPI), you
    know that it's already fairly easy to extract configuration data from your
    EOS nodes, but this library seeks to make configuration validation possible
    for those who have no programming experience.  You'll notice that this library
    utilizes [https://github.com/arista-eosplus/pyeapi|pyeapi], which greatly
    simplifies the retreival and analysis of EOS configuration.  We encourage
    you to participate in the development of this library by visiting
    [https://github.com/arista-eosplus|AristaLibrary], hosted on Github.

    Note: This library has been built for Python only.

    == Table of contents ==

    - `Installing the library`
    - `Examples`

    = Installing the library =
    You can get the AristaLibrary using PIP
    | pip install robotframework-aristalibrary

    or install from source
    | <add source code link here once moved to GitHub>

    = Examples =
    == Connecting to a test node ==
    == Switching between connected nodes ==
    == Testing the EOS Software version ==

    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, transport="https", host='localhost',
                 username="admin", password="admin", port="443", alias=None):
        """Defaults may be changed by specifying when importing the library:
        | *** Setting ***
        | Library AristaLibrary
        | Library AristaLirary | username="apiuser" | password="donttell"
        """
        self.host = host
        self.transport = transport
        self.port = port
        self.username = username
        self.password = password
        self.alias = None
        self.connections = dict()
        self._connection = ConnectionCache()

    # ---------------- Start Core Keywords ---------------- #

    def connect_to(self, host='localhost', transport='https', port='443',
                   username='admin', password='admin', alias=None,
                   autorefresh=True):

        """This is the cornerstone of all testing. The Connect To
        keyword accepts the necessary parameters to setup an API connection to
        your node.

        Example:
        | Connect To | host=192.0.2.50 | transport=http | port=80 | username=myUser | password=secret |
        | Connect To | host=192.0.2.51 | username=myUser | password=secret |

        This function returns a connection index, which can be used to change
        connections during a test suite. Example:

        | ${switch1}= | Connect To | host=192.0.2.51 | username=myUser | password=secret |

        You can confirm which interface eAPI is listening on by running:
        | veos-node>show management api http-commands
        | *Enabled:        Yes*
        | *HTTPS server:   running, set to use port 443*
        | HTTP server:    shutdown, set to use port 80
        | VRF:            default
        | Hits:           28
        | Last hit:       2128 seconds ago
        | Bytes in:       1547
        | Bytes out:      283966
        | Requests:       1
        | Commands:       1
        | Duration:       0.055 seconds
        |    User        Hits       Bytes in       Bytes out    Last hit
        | ----------- ---------- -------------- --------------- ----------------
        |   admin       1          1547           283966       2128 seconds ago
        |
        | URLs
        | ---------------------------------------
        | *Management1 : https://192.0.2.50:443*

        You can confirm connectivity by firing up a browser and point it to
        https://<my_url>:<my_port>/command-api

        If you are new to eAPI see the Arista EOS Central article,
        [https://eos.arista.com/arista-eapi-101|Arista eAPI 101]
        """

        host = str(host)
        transport = str(transport)
        port = int(port)
        username = str(username)
        password = str(password)
        if alias:
            alias = str(alias)
        try:
            client = pyeapi.connect(
                host=host, transport=transport,
                username=username, password=password, port=port)
            client_node = pyeapi.client.Node(client)
            client_node.autorefresh = autorefresh
            conn_indx = self._connection.register(client_node, alias)
        except Exception as e:
            raise e

        # Always try "show version" when connecting to a node so that if
        #  there is a configuration error, we can fail quickly.
        try:
            ver = self._connection.current.enable(
                ['show version'])[0]['result']
            mesg = "Created connection to {}://{}:{}@{}:{}/command-api: model: {}, serial: {}, systemMAC: {}, version: {}, lastBootTime: {}".format(
                transport, username, '****', host, port,
                ver['modelName'], ver['serialNumber'], ver['systemMacAddress'],
                ver['version'], ver['bootupTimestamp'])
            logger.write(mesg, 'INFO', False)
        except Exception as e:
            raise e

        self.connections[conn_indx] = dict(conn=client,
                                           node=client_node,
                                           index=conn_indx,
                                           transport=transport,
                                           host=host,
                                           username=username,
                                           password=password,
                                           port=port,
                                           alias=alias,
                                           autorefresh=autorefresh)
        return conn_indx

    def change_to_switch(self, index_or_alias):
        # TODO update docstring
        """Change To Switch changes the active switch for all following keywords.

        Arguments:
        - `index_or_alias`: The connection index (integer) or the alias (string)
        of the desired connection.

        Returns the index of the previous connection which can be stored for reuse.

        Example:
        | ${uut1}=                | Connect To       | ...           |
        | ${uut2}=                | Connect To       | alias=foo ... |
        | Configure hostname uut2 |                  |               |
        | ${previous}=            | Change To Switch | ${uut1}       |
        | ${ver_info}=            | Run Commands     | show version  |
        | Change To Switch        | ${previous}      |               |
        | Change To Switch        | foo              |               |
        """

        old_index = self._connection.current_index
        self._connection.switch(index_or_alias)
        return old_index

    def clear_all_connections(self):
        """ Remove all connection objects from the cache and resets the list of
        indexes.
        """
        self.host = 'localhost'
        self.transport = 'https'
        self.port = '443'
        self.username = 'admin'
        self.password = 'admin'
        self.connections = dict()
        # Since we don't really have anything to close, just delete entries.
        #self._connection.close_all()
        self._connection.empty_cache()

    def get_switch(self, index_or_alias=None):
        """ Get Switch returns a dictionary of information about the active
        switch connection. Details include the host, username, password,
        transport and port.

        Example:
        | ${uut1}         | Connect To                               | ....               |
        | ${switch_info}= | Get Switch                               |                    |
        | ${switch_info}= | Get Switch                               | index_or_alias=2   |
        | ${switch_info}= | Get Switch                               | index_or_alias=foo |
        | Log             | Connected to port ${switch_info['port']} |                    |
        """

        if not index_or_alias:
            index_or_alias = self._connection.current_index
        #values = self.connections[index_or_alias]
        try:
            values = self.connections[self._connection._resolve_alias_or_index(index_or_alias)]
        except (ValueError, KeyError):
            values = {'index': None,
                      'alias': None
                     }
        return values

    def get_switches(self):
        """
        The Get Switches keyword returns a list of all nodes that are
        in your cache. It will return the host, username, password,
        port, transport.

        Example:
        | ${uut1}         | Connect To                                               | .... |
        | ${uut2}         | Connect To                                               | .... |
        | @{switch_info}= | Get Switches                                             |      |
        | Log             | First switch connected to port ${switch_info[0]['port']} |      |
        """
        return_value = list()
        for indx, values in self.connections.items():
            return_value.append(values)
        return return_value

    # ---------------- End Core Keywords ---------------- #

    # ---------------- Start Analysis Keywords ---------- #

    def run_cmds(self, commands, format='json'):
        """Run Cmds allows low-level access to run any eAPI command against your
        switch and then process the output using Robot's builtin keywords.

        Arguments:
        - commands: This must be the full eAPI command. command may not the
        short form that works on the CLI.

        Example:

        Good:
        | show version
        Bad:
        | sho ver

        - `format` is the format that the text will be returned from the API
        request. The two options are 'text' and 'json'. Note that EOS does not
        support a JSON response for all commands. Please refer to your EOS
        Command API documentation for more details.

        Examples:
        | ${json_dict}= | Run Cmds | show version                |             |
        | ${raw_text}=  | Run Cmds | show interfaces description | format=text |
        """
        try:
            commands = make_iterable(commands)
            client = self.connections[self._connection.current_index]['conn']
            return client.execute(commands, format)
        except CommandError as e:
            error = ""
            # This just added by Peter in pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def run_commands(self, command, all_info=False):
        # TODO: Jere update me
        """Run Commands allows you to run any eAPI command against your
        switch and then process the output using Robot's builtin keywords.  It
        will automatically ensure the CLI is in `enable` mode prior to executing
        the command(s).

        Arguments:
        - `commands`: This must be the full eAPI command and not the short form
        that works on the CLI.  `commands` may be a single command or a list of
        commands.  When passing a list to Run Commands, it should be given as a
        scalar.

        Example:

        Good:
        | show version
        Bad:
        | sho ver

        - format: This is the format that the text will be returned from the API
        request. The two options are 'text' and 'json'. Note that EOS does not
        support a JSON response for all commands. Please refer to your EOS
        Command API documentation for more details.

        Examples:
        | ${json_dict}= | Run Commands | show version                |               |
        | ${raw_text}=  | Run Commands | show interfaces description | all_info=True |
        | @{commands}=  | show version | show interfaces Ethernet 1  |               |
        | ${json_dict}= | Run Commands | ${commands}                 |               |
        """
        try:
            if all_info:
                return self._connection.current.enable(
                    [command])
            return self._connection.current.enable(
                [command])[0]['result']
        except CommandError as e:
            error = ""
            # This just added by Peter to pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def enable(self, command):
        try:
            return self._connection.current.enable([command])
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def get_startup_config(self):
        try:
            return self._connection.current.startup_config
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def get_running_config(self):
        try:
            return self._connection.current.running_config
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def config(self, commands):
        try:
            return self._connection.current.config(commands)
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    configure = config

    def version_should_contain(self, version):
        """Version Should Contain compares the EOS version running on your node
        with the string provided.
        It is flexible in that it does not require an exact match -
        e.g. 4.14 == 4.14.0F.

        Example:
        | Version Should Contain | 4.14.0F |

        This keyword evaluates the 'Software image version' from 'Show Version'
        Example:
        | veos-node# show version
        | Arista vEOS
        | Hardware version:
        | Serial number:
        | System MAC address:  0011.2233.4455
        |
        | *Software image version: 4.14.2F*
        | Architecture:           i386
        | Internal build version: 4.14.2F-2083164.4142F.1
        | Internal build ID:      19fe6cb3-1777-40b6-a4e6-53875b30658c
        |
        | Uptime:                 21 hours and 59 minutes
        | Total memory:           2028804 kB
        | Free memory:            285504 kB
        """
        try:
            out = self._connection.current.enable(['show version'])[0]['result']
            version_number = str(out['version'])
        except Exception as e:
            raise e
            return False
        if not re.search(str(version), version_number):
            raise AssertionError('Searched for %s, Found %s'
                                 % (str(version), version_number))
        return True

    def list_extensions(self, available='any', installed='any'):
        """List Extensions returns a list with the name of each
        extension present on the node.

        Arguments:
        *available*: By default this is 'any', meaning the available status of \
        the extension will not be used to filter to output.

        Only return 'Available' extensions:
        | available=True
        Only return 'Not Available' extensions
        | available=False

        *installed*: By default this is 'any', meaning the installed status of \
        the extension will not be used to filter to output.

        Only return 'Installed' extensions:
        | installed=True
        Only return 'Not Installed' extensions
        | installed=False
        Only return extensions which were installed by force:
        | installed="forced"

        Sample 'Show Version' output from the CLI:

        | Name                                       Version/Release           Status extension
        | ------------------------------------------ ------------------------- ------ ----
        | eos-puppet-conf-0.1-1.eos4.noarch.rpm      0.1/1.eos4                A, I      1
        | puppet-3.7.1-3-ruby2.swix                  3.7.1/1.eos4              A, I     14
        | ruby-2.0.0-1.swix                          2.0.0.353/16.fc14         A, I     11
        |
        | A: available | NA: not available | I: installed | NI: not installed | F: forced

        Note: If you want all data pertaining to the extensions use the Get
        Extensions keyword.
        """
        # Confirm parameter values are acceptable
        if available not in [True, False, 'any']:
            raise AssertionError('Incorrect parameter value: %s. '
                                 'Choose from [True|False|any]' % available)

        if installed not in [True, False, 'forced', 'any']:
            raise AssertionError('Incorrect parameter value: %s. '
                                 'Choose from [True|False|forced|any]' % installed)

        try:
            out = self._connection.current.enable(['show extensions'])
            out = out[0]
        except Exception as e:
            raise e

        if out['encoding'] == 'json':
            extensions = out['result']['extensions']
            filtered = []
            for ext, data in extensions.items():
                if available == True and data['presence'] != 'present':
                    continue
                elif available == False and data['presence'] == 'present':
                    continue

                if installed == True and data['status'] != 'installed':
                    continue
                elif installed == "forced" and data['status'] != 'forceInstalled':
                    continue
                elif installed == False and data['status'] != 'notInstalled':
                    continue

                # If all of the checks above pass then we can append the
                # extension to the list
                filtered.append(ext)

            return filtered
