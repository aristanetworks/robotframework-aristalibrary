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
        self.connections = list()
        self.active = None

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
        self.connections.append(self.active)
        return self.active

    def version_should_be(self, version):
        try:
            out = self.active.execute(['show version'])
            version_number = str(out['result'][0]['version'])
        except Exception as e:
            raise e
            return False
        if not re.search(str(version), version_number):
            raise AssertionError('Version did not match')
        return True

    def execute(self, command):
        try:
            return self.active.execute([command])
        except Exception as e:
            print e

    def clear_all_connection(self):
        self.hostname = 'localhost'
        self.proto = 'https'
        self.port = '443'
        self.username = 'admin'
        self.passwd = 'admin'
        self.conn = []
        self.active = None
