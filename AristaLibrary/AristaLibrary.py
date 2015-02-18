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
        self._connectiontest = ConnectionCache()

    def connect_to(self, host='localhost', transport='https', port='443',
                   username='admin', password='admin', alias=None):
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
            conn_indx = self._connectiontest.register(client, alias)
        except Exception as e:
            print e
            return False
        self.connections[conn_indx] = dict(conn=client,
                                           transport=transport,
                                           host=host,
                                           username=username,
                                           password=password,
                                           port=port,
                                           alias=alias)
        return conn_indx

    def version_should_contain(self, version):
        try:
            out = self._connectiontest.current.execute(['show version'])
            version_number = str(out['result'][0]['version'])
        except Exception as e:
            raise e
            return False
        if not re.search(str(version), version_number):
            raise AssertionError('Searched for %s, Found %s'
                                 % (str(version), version_number))
        return True

    def run_cmds(self, command):
        try:
            return pyeapi.client.Node(self._connectiontest.current).enable(
                [command])[0]['result']
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def change_to_switch(self, index_or_alias):
        old_index = self._connectiontest.current_index
        self._connectiontest.switch(index_or_alias)
        return old_index

    def get_switch(self):
        host = self.connections[self._connectiontest.current_index]['host']
        username = \
            self.connections[self._connectiontest.current_index]['username']
        password = \
            self.connections[self._connectiontest.current_index]['password']
        transport = \
            self.connections[self._connectiontest.current_index]['transport']
        port = self.connections[self._connectiontest.current_index]['port']
        alias = self.connections[self._connectiontest.current_index]['alias']
        return_value = host, username, password, transport, port, alias
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
            info = host, username, password, transport, port, alias
            return_value.append(info)
        return return_value

    def enable(self, command):
        try:
            return pyeapi.client.Node(self._connectiontest.current).enable(
                [command])
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def clear_all_connection(self):
        self.host = 'localhost'
        self.transport = 'https'
        self.port = '443'
        self.username = 'admin'
        self.password = 'admin'
        self.connections = dict()
        self._connectiontest.close_all()
