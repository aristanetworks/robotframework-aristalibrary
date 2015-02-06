import pyeapi


class AristaLibrary:
    def __init__(self, proto="https", hostname='localhost',
                 username="admin", passwd="admin", port="443"):
        self.hostname = hostname
        self.proto = proto
        self.port = port
        self.username = username
        self.passwd = passwd

    def connect_to(self, proto, hostname, username, passwd, port):
        proto = str(proto)
        hostname = str(hostname)
        username = str(username)
        passwd = str(passwd)
        port = str(port)
        node = pyeapi.connect(proto, hostname, username, passwd, port)
        return node

    def enable(self, conn, command):
        return conn.execute([command])

