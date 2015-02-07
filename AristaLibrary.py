import pyeapi


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

    def execute(self, command):
        return self.conn.execute([command])

    def clear_all_connection(self):
        self.hostname = 'localhost'
        self.proto = 'https'
        self.port = '443'
        self.username = 'admin'
        self.passwd = 'admin'
        self.conn = None
