#
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
import re


class AristaLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, transport="https", host='localhost',
                 username="admin", password="admin", port="443"):
        self.host = host
        self.transport = transport
        self.port = port
        self.username = username
        self.password = password
        self.connections = dict()
        self.active = None
        self.active_node = None

    def connect_to(self, host='localhost', transport='https', port='443',
                   username='admin', password='admin'):
        host = str(host)
        transport = str(transport)
        port = int(port)
        username = str(username)
        password = str(password)
        try:
            self.active = pyeapi.connect(
                host=host, transport=transport,
                username=username, password=password, port=port)
            self.active_node = pyeapi.client.Node(self.active)
            # self.active_node.enable(['show version'])
        except Exception as e:
            print e
            return False
        self.connections[host] = dict(conn=self.active,
                                      node=self.active_node,
                                      transport=transport,
                                      host=host,
                                      username=username,
                                      password=password,
                                      port=port)
        self.current_ip = host

        # Always try "show version" when connecting to a node so that if
        #  there is a configuration error, we can fail quickly.
        try:
            # self.active_node.enable(['show version'])
            json = self.active.execute(['show version'])
            ver = json['result'][0]
            mesg = "Created connection to {}://{}:{}@{}:{}/command-api: model: {}, serial: {}, systemMAC: {}, version: {}, lastBootTime: {}".format(
                transport, username, '****', host, port,
                ver['modelName'], ver['serialNumber'], ver['systemMacAddress'],
                ver['version'], ver['bootupTimestamp'])
            logger.write(mesg, 'INFO', False)
        except CommandError as e:
            error = ""
            # This just added by Peter to pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))
        return self.active

    def version_should_contain(self, version):
        try:
            out = self.active.execute(['show version'])
            version_number = str(out['result'][0]['version'])
        except Exception as e:
            raise e
            return False
        if not re.search(str(version), version_number):
            raise AssertionError('Searched for %s, Found %s'
                                 % (str(version), version_number))
        return True

    def run_cmds(self, commands, format='json'):
        try:
            commands = make_iterable(commands)
            return self.active.execute(commands, format)
        except CommandError as e:
            error = ""
            # This just added by Peter in pyeapi 10 Feb 2015
            # if self.active_node.connection.error.command_error:
            #     error = self.active_node.connection.error.command_error
            raise AssertionError('eAPI CommandError: {}\n{}'.format(e, error))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def change_to_switch(self, ip):
        self.active = self.connections[ip]['conn']
        self.active_node = self.connections[ip]['node']
        self.current_ip = ip

    def get_switch(self):
        host = self.connections[self.current_ip]['host']
        username = self.connections[self.current_ip]['username']
        password = self.connections[self.current_ip]['password']
        transport = self.connections[self.current_ip]['transport']
        port = self.connections[self.current_ip]['port']
        return_value = host, username, password, transport, port
        return return_value

    def get_switches(self):
        return_value = list()
        for name, values in self.connections.items():
            host = values['host']
            username = values['username']
            password = values['password']
            port = values['port']
            transport = values['transport']
            info = host, username, password, transport, port
            return_value.append(info)
        return return_value

    def clear_all_connection(self):
        self.host = 'localhost'
        self.transport = 'https'
        self.port = '443'
        self.username = 'admin'
        self.password = 'admin'
        self.conn = []
        self.active = None
        self.active_node = None
        self.current_ip = ''
        self.connections = dict()
