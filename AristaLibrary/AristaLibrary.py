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
from version import VERSION
import re


class AristaLibrary(object):
    """AristaLibrary - A Robot Framework Library for testing Arista EOS Devices.

    The AristaLibrary has been designed to simplify the task of configuration
    validation and verification. If you are familiar with Command-API(eAPI),
    you know that it's already fairly easy to extract configuration data from
    your EOS nodes, but this library seeks to make configuration validation
    possible for those who have no programming experience.  You'll notice that
    this library utilizes [https://github.com/arista-eosplus/pyeapi|pyeapi],
    which greatly simplifies the retreival and analysis of EOS configuration.
    We encourage you to participate in the development of this library by
    visiting [https://github.com/aristanetworks/robotframework-aristalibrary|AristaLibrary], hosted on
    Github.

    Note: This library has been built for Python only.

    == Table of contents ==

    - `Installing the library`
    - `Examples`

    = Installing the library =
    You can get the AristaLibrary using PIP
    | pip install robotframework-aristalibrary

    or install from source
    | git clone https://github.com/aristanetworks/robotframework-aristalibrary.git
    | cd robotframework-aristalibrary/
    | python setup.py install

    = Examples =
    == Connecting to a test node ==
    == Switching between connected nodes ==
    == Testing the EOS Software version ==

    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

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
                   enablepwd=None, autorefresh=True):

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
            client_node.enable_authentication(enablepwd)
            conn_indx = self._connection.register(client_node, alias)
        except Exception as e:
            raise e

        # Always try "show version" when connecting to a node so that if
        #  there is a configuration error, we can fail quickly.
        try:
            ver = self._connection.current.enable(
                ['show version'])[0]['result']
            mesg = "Created connection to {}://{}:{}@{}:{}/command-api: "\
                "model: {}, serial: {}, systemMAC: {}, version: {}, "\
                "lastBootTime: {}".format(
                    transport, username, '****', host, port,
                    ver['modelName'], ver['serialNumber'],
                    ver['systemMacAddress'],
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
        - `index_or_alias`: The connection index (integer) or the alias
        (string) of the desired connection.

        Returns the index of the previous connection which can be stored for
        reuse.

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
        # self._connection.close_all()
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
        # values = self.connections[index_or_alias]
        try:
            values = self.connections[
                self._connection._resolve_alias_or_index(index_or_alias)
            ]
        except (ValueError, KeyError):
            values = {
                'index': None,
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

    def run_cmds(self, commands, encoding='json'):
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

        - `encoding` is the format of the response will be returned from the API
        request. The two options are 'text' and 'json'. Note that EOS does not
        support a JSON response for all commands. Please refer to your EOS
        Command API documentation for more details.

        Examples:
        | ${json_dict}= | Run Cmds | show version                |               |
        | ${raw_text}=  | Run Cmds | show interfaces description | encoding=text |
        """
        if isinstance(commands, basestring):
            commands = [str(commands)]
        elif isinstance(commands, list):
            # Handle Python2 unicode strings
            for idx, command in enumerate(commands):
                if isinstance(command, unicode):
                    commands[idx] = str(command)

        try:
            commands = make_iterable(commands)
            client = self.connections[self._connection.current_index]['conn']
            return client.execute(commands, encoding)
        except CommandError as e:
            error = ""
            # This just added by Peter in pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def run_commands(self, commands, all_info=False, encoding='json'):
        # TODO: Jere update me
        """Run Commands allows you to run any eAPI command against your
        switch and then process the output using Robot's builtin keywords.  It
        will automatically ensure the CLI is in `enable` mode prior to
        executing the command(s).

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

        - format: This is the format that the text will be returned from the
        API request. The two options are 'text' and 'json'. Note that EOS does
        not support a JSON response for all commands. Please refer to your EOS
        Command API documentation for more details.

        Examples:
        | ${json_dict}= | Run Commands | show version                |               |
        | ${raw_text}=  | Run Commands | show interfaces description | all_info=True |
        | @{text}=      | show version | show interfaces Ethernet 1  | encoding=text |
        | @{commands}=  | show version | show interfaces Ethernet 1  |               |
        | ${json_dict}= | Run Commands | ${commands}                 |               |
        """
        if isinstance(commands, basestring):
            commands = [str(commands)]
        elif isinstance(commands, list):
            # Handle Python2 unicode strings
            for idx, command in enumerate(commands):
                if isinstance(command, unicode):
                    commands[idx] = str(command)

        try:
            if all_info:
                return self._connection.current.enable(
                    [commands], encoding)
            return self._connection.current.enable(
                [commands], encoding)[0]['result']
        except CommandError as e:
            error = ""
            # This just added by Peter to pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def enable(self, commands, encoding='json'):
        """
        The Enable keyword lets you run a list of commands in enable mode.
        It returns a list containing the list of commands, output of those
        commands and the encoding used. It uses the pyeapi Node.enable()
        function. If a command fails due to an encoding error, then the command
        set will be re-issued individual with text encoding.

        Arguments:
        - `command`: This must be the full eAPI command and not the short form
        that works on the CLI.  `commands` may be a single command or a list of
        commands.  When passing a list to Run Commands, it should be given as a
        scalar.


        Example:
        | @{list_v}=        | Create List | show version | show hostname |
        | ${enable}=        | Enable      | ${list_v}    |               |
        """

        if isinstance(commands, basestring):
            commands = [str(commands)]
        elif isinstance(commands, list):
            # Handle Python2 unicode strings
            for idx, command in enumerate(commands):
                if isinstance(command, unicode):
                    commands[idx] = str(command)

        try:
            return self._connection.current.enable(commands, encoding)
        except CommandError as e:
            raise AssertionError('eAPI enable CommandError:'
                                 ' {} {}'.format(e, commands))
        except Exception as e:
            raise AssertionError('eAPI enable execute command: {}'.format(e))

    def get_startup_config(self, section=None):
        """
        The Get Startup Config keyword retrieves the startup config from
        the node as a string.

        Arguments:
        - 'section' (regex): If supplied, the section regex will be matched
        to return the indicated block of the startup config. If omitted,
        Get Startup Config returns the entire startup config.

        Example:
        | ${startup}=        | Get Startup Config |
        | ${startup}=        | Get Startup Config | section=^management api http-commands$
        | ${startup}=        | Get Startup Config | section=^interface Ethernet1
        | ${startup}=        | Get Startup Config | ^interface Ethernet2
        """

        if section:
            try:
                return self._connection.current.section(
                    section, config='startup_config')
            except CommandError as e:
                raise AssertionError('Pyeapi error getting startup-config: {}'
                                     .format(e))
            except Exception as e:
                raise AssertionError('eAPI execute command: {}'.format(e))
        else:
            try:
                return self._connection.current.startup_config
            except CommandError as e:
                raise AssertionError('Pyeapi error getting startup-config: {}'
                                     .format(e))
            except Exception as e:
                raise AssertionError('eAPI execute command: {}'.format(e))

    def get_running_config(self, section=None):
        """
        The Get Running Config keyword retrieves the running config from
        the node as a string.

        Arguments:
        - 'section' (regex): If supplied, the section regex will be matched
        to return the indicated block of the running config. If omitted,
        Get Running Config returns the entire running config.

        Example:
        | ${running}=        | Get Running Config |
        | ${running}=        | Get Running Config | section=^management api http-commands$
        | ${running}=        | Get Running Config | section=^interface Ethernet1
        | ${running}=        | Get Running Config | ^interface Ethernet2
        """

        if section:
            try:
                return self._connection.current.section(section)
            except CommandError as e:
                raise AssertionError('Pyeapi error getting running-config: {}'
                                     .format(e))
            except Exception as e:
                raise AssertionError('eAPI execute command: {}'.format(e))
        else:
            try:
                return self._connection.current.running_config
            except CommandError as e:
                raise AssertionError('Pyeapi error getting running-config: {}'
                                     .format(e))
            except Exception as e:
                raise AssertionError('eAPI execute command: {}'.format(e))

    def config(self, commands):
        """
        The Config keyword lets you configures the node with the specified
        commands. This method is used to send configuration commands to the
        node.  It will take either a string or a list and prepend the necessary
        commands to put the session into config mode.

        Arguments:
        - `command` (str, list): The commands to send to the node in config
        mode.  If the commands argument is a string it will be cast to
        a list.  The list of commands will also be prepended with the
        necessary commands to put the session in config mode.


        Example:
        | @{commands}=      | Create List | show version | show hostname |
        | ${config}=        | Config      | ${commands}  |               |
        """

        if isinstance(commands, basestring):
            commands = [commands]

        try:
            return self._connection.current.config(commands)
        except CommandError as e:
            raise AssertionError('eAPI config CommandError:'
                                 ' {} {}'.format(e, commands))
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
                                 'Choose from [True|False|forced|any]' %
                                 installed)

        try:
            out = self._connection.current.enable(['show extensions'])
            out = out[0]
        except Exception as e:
            raise e

        if out['encoding'] == 'json':
            extensions = out['result']['extensions']
            filtered = []
            for ext, data in extensions.items():
                if available and data['presence'] != 'present':
                    continue
                elif not available and data['presence'] == 'present':
                    continue

                if installed and data['status'] is not 'installed':
                    continue
                elif installed == "forced" and data['status'] != \
                        'forceInstalled':
                    continue
                elif not installed and \
                        data['status'] != 'notInstalled':
                    continue

                # If all of the checks above pass then we can append the
                # extension to the list
                filtered.append(ext)

            return filtered

    def refresh(self):
        """Refreshes the instance config properties
        This method will refresh the public running_config and startup_config
        properites of the currently active switch.  Since the properties are
        lazily loaded, this method will clear the current internal instance
        variables.  On the next call the instance variables will be
        repopulated with the current config

        Example:
        | Connect To                   | host=192.0.2.50         | transport=http        | port=80         | username=myUser | password=secret | autorefresh=False |
        | @{commands}=                 | Create List             | hostname newhostname  |                 |                 |                 |                   |
        | ${config}=                   | Config                  | ${commands}           |                 |                 |                 |                   |
        | ${before_refresh}=           | Get Running Config      |                       |                 |                 |                 |                   |
        | LOG                          | ${before_refresh}       | level=DEBUG           |                 |                 |                 |                   |
        | ${after_refresh}=            | Get Running Config      |                       |                 |                 |                 |                   |
        | LOG                          | ${after_refresh}        | level=DEBUG           |                 |                 |                 |                   |  # NOQA

        | ${before_refresh} = ! Command: show running-config
        | ! device: vEOS1 (vEOS, EOS-4.14.0F)
        | !
        | ! boot system flash:/vEOS-4.14.0F.swi
        | !
        | alias ztpprep bash sudo /mnt/flash/ztpprep
        | !
        | event-handler configpush
        |    trigger on-s...


        | ${after_refresh} = ! Command: show running-config
        | ! device: newhostname (vEOS, EOS-4.14.0F)
        | !
        | ! boot system flash:/vEOS-4.14.0F.swi
        | !
        | alias ztpprep bash sudo /mnt/flash/ztpprep
        | !
        | event-handler configpush
        |    trigger on-s...
        """

        self._connection.current.refresh()

    def ping_test(self, address, vrf='default', source_int=None):
        """
        The Ping Test keyword pings the provided IP address from current device
        and returns the packet loss percentage.

        Arguments:
        - `address`: A text string identifying IP address to ping from the
        current switch.
        - `vrf`: A text string identifying the VRF to execute the ping within.

        Example:
        | ${loss_percent}=  | Ping Test         | 10.0.0.10     |
        | LOG               | ${loss_percent}   | level=DEBUG   |
        | ${loss_percent}=  | Ping Test         | 1.1.1.1       | mgmt  |

        This keyword parses and returns the loss percentage from the 'Ping'
        command. Example below would return 0.
        Example:
        | veos-node#ping vrf default 10.0.0.10
        | PING 10.0.0.10 (10.0.0.10) 72(100) bytes of data.
        | 80 bytes from 10.0.0.10: icmp_seq=1 ttl=64 time=18.7 ms
        | 80 bytes from 10.0.0.10: icmp_seq=2 ttl=64 time=21.3 ms
        | 80 bytes from 10.0.0.10: icmp_seq=3 ttl=64 time=22.4 ms
        | 80 bytes from 10.0.0.10: icmp_seq=4 ttl=64 time=21.5 ms
        | 80 bytes from 10.0.0.10: icmp_seq=5 ttl=64 time=20.9 ms
        |
        | --- 10.0.0.10 ping statistics ---
        | 5 packets transmitted, 5 received, 0% packet loss, time 78ms
        | rtt min/avg/max/mdev = 18.771/20.999/22.424/1.231 ms, pipe 2, ipg/ewma 19.584/19.907 ms
        """
        source = ''
        if source_int:
            source = ' source %s' % source_int
        try:
            out = self._connection.current.enable(
                ['ping vrf %s %s%s' % (vrf, address, source)], encoding='text')
            out = out[0]['result']
        except Exception as e:
            raise e

        pattern = r'(\d+)% packet loss'
        match = re.search(pattern, out['output'])
        if not match or not match.group(1):
            raise AssertionError('No packet loss percentage found'
                                 ' in output %s.' % out['output'])
        return match.group(1)

    def address_is_reachable(self, address, vrf='default', source_int=None):
        """
        The Address Is Reachable keyword checks if the provided IP address
        is reachable from the current device. The address is considered
        reachable if the ping result does not have 100% packet loss.

        Arguments:
        - `address`: A text string identifying IP address to ping from the
        current switch.
        - `vrf`: A text string identifying the VRF to execute the ping within.

        Example:
        | ${reachable}=     | Address Is Reachable  | 1.1.1.1   |
        | ${reachable}=     | Address Is Reachable  | 1.1.1.1   | mgmt  |
        """
        loss_percent = self.ping_test(address, vrf, source_int)
        if loss_percent == '100':
            return False
        return True
