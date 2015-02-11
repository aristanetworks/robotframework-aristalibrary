import pyeapi
from pyeapi.eapilib import CommandError
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
        except Exception as e:
            print e
            return False
        self.connections[host] = dict(conn=self.active,
                                          transport=transport,
                                          host=host,
                                          username=username,
                                          password=password,
                                          port=port)
        self.current_ip = host
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

    def run_cmds(self, command):
        try:
            return self.active.execute([command])
        except CommandError as e:
            raise AssertionError('eAPI CommandError: {}'.format(e))
        except Exception as e:
            raise AssertionError('eAPI execute command: {}'.format(e))

    def change_to_switch(self, ip):
        self.active = self.connections[ip]['conn']
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
        self.current_ip = ''
        self.connections = dict()
