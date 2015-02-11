import pyeapi
import re


class AristaLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, proto="https", hostname='localhost',
                 username="admin", passwd="admin", port="443"):
        self.hostname = hostname
        self.proto = proto
        self.port = port
        self.username = username
        self.passwd = passwd
        self.connections = dict()
        self.active = None
        self.current_ip = ''

    def connect_to(self, proto, hostname, username, passwd, port):
        proto = str(proto)
        hostname = str(hostname)
        username = str(username)
        passwd = str(passwd)
        port = str(port)
        try:
            self.active = pyeapi.connect(
                proto, hostname, username, passwd, port)
        except Exception as e:
            print e
            return False
        self.connections[hostname] = dict(conn=self.active,
                                          proto=proto,
                                          hostname=hostname,
                                          username=username,
                                          passwd=passwd,
                                          port=port)
        self.current_ip = hostname
        return self.active

    def version_should_be(self, version):
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
        except Exception as e:
            print e

    def change_to_switch(self, ip):
        self.active = self.connections[ip]['conn']
        self.current_ip = ip

    def get_switch(self):
        hostname = self.connections[self.current_ip]['hostname']
        username = self.connections[self.current_ip]['username']
        passwd = self.connections[self.current_ip]['passwd']
        proto = self.connections[self.current_ip]['proto']
        port = self.connections[self.current_ip]['port']
        return_value = hostname, username, passwd, proto, port
        return return_value

    def clear_all_connection(self):
        self.hostname = 'localhost'
        self.proto = 'https'
        self.port = '443'
        self.username = 'admin'
        self.passwd = 'admin'
        self.conn = []
        self.active = None
        self.current_ip = ''
        self.connections = dict()
