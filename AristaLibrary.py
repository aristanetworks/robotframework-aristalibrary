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
        self.conn = None

    def connect_to(self, proto, hostname, username, passwd, port):
        proto = str(proto)
        hostname = str(hostname)
        username = str(username)
        passwd = str(passwd)
        port = str(port)
        self.conn = pyeapi.connect(proto, hostname, username, passwd, port)
        return self.conn

    def version_should_be(self, version):
        try:
            out = self.conn. execute(['show version'])
        except Exception as e:
            print e
        version_number = str(out['result'][0]['version'])
        if not re.search(version_number, str(version)):
            raise AssertionError('Version did not match')
        return True

    def execute(self, command):
        return self.conn.execute([command])

    def clear_all_connection(self):
        self.hostname = 'localhost'
        self.proto = 'https'
        self.port = '443'
        self.username = 'admin'
        self.passwd = 'admin'
        self.conn = None
