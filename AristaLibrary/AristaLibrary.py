import pyeapi
from pyeapi.eapilib import CommandError
from robot.utils import ConnectionCache
import re


class AristaLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, transport="https", host='localhost',
                 username="admin", password="admin", port="443", alias=None):
        self.host = host
        self.transport = transport
        self.port = port
        self.username = username
        self.password = password
        self.alias = None
        self.connections = dict()
        self._connection = ConnectionCache()

    def connect_to(self, host='localhost', transport='https', port='443',
                   username='admin', password='admin', alias=None,
                   autorefresh=True):
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
            print e
            return False
        self.connections[conn_indx] = dict(conn=client,
                                           transport=transport,
                                           host=host,
                                           username=username,
                                           password=password,
                                           port=port,
                                           alias=alias,
                                           autorefresh=autorefresh)
        return conn_indx

    def version_should_contain(self, version):
        try:
            out = self._connection.current.enable(
                ['show version'])[0]['result']
            version_number = str(out['version'])
        except Exception as e:
            raise e
            return False
        if not re.search(str(version), version_number):
            raise AssertionError('Searched for %s, Found %s'
                                 % (str(version), version_number))
        return True

    def run_commands(self, command, all_info=False):
        try:
            if all_info:
                return self._connection.current.enable(
                    [command])
            return self._connection.current.enable(
                [command])[0]['result']
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def change_to_switch(self, index_or_alias):
        old_index = self._connection.current_index
        self._connection.switch(index_or_alias)
        return old_index

    def get_switch(self):
        host = self.connections[self._connection.current_index]['host']
        username = \
            self.connections[self._connection.current_index]['username']
        password = \
            self.connections[self._connection.current_index]['password']
        transport = \
            self.connections[self._connection.current_index]['transport']
        port = self.connections[self._connection.current_index]['port']
        alias = self.connections[self._connection.current_index]['alias']
        autorefresh = \
            self.connections[self._connection.current_index]['autorefresh']
        return_value = \
            host, username, password, transport, port, alias, autorefresh
        return return_value

    def get_switches(self):
        return_value = list()
        for name, values in self.connections.items():
            host = values['host']
            username = values['username']
            password = values['password']
            port = values['port']
            transport = values['transport']
            alias = values['alias']
            autorefresh = values['autorefresh']
            info = \
                host, username, password, transport, port, alias, autorefresh
            return_value.append(info)
        return return_value

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

    def clear_all_connection(self):
        self.host = 'localhost'
        self.transport = 'https'
        self.port = '443'
        self.username = 'admin'
        self.password = 'admin'
        self.connections = dict()
        self._connection.close_all()
