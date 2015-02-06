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
        node = pyeapi.connect(proto, hostname, username, passwd, port)
        out = node.execute(['show version'])
        return out

    def enable(self, conn, command):
        return conn.execute([command])

arista = AristaLibrary()
node = arista.connect_to('https', '10.68.49.140', 'admin', 'admin', '443')
#out = arista.enable(node, 'show version')
print node
