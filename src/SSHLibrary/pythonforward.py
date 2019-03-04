import select
import threading
from robot.utils import platform
if platform.PY2 and platform.WINDOWS:
    import win_inet_pton
import socket

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


def check_if_ipv6(ip):
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        return False


class LocalPortForwarding:
    def __init__(self, port, host, transport, bind_address):
        self.server = None
        self.port = port
        self.host = host
        self.transport = transport
        self.bind_address = bind_address

    def forward(self, local_port):
        class SubHandler(LocalPortForwardingHandler):
            port = self.port
            host = self.host
            ssh_transport = self.transport

        self.server = ForwardServer((self.bind_address or '', local_port), SubHandler, ipv6=check_if_ipv6(self.host))
        t = threading.Thread(target=self.server.serve_forever)
        t.setDaemon(True)
        t.start()

    def close(self):
        if self.server:
            self.server.shutdown()


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, ipv6=False):
        if ipv6:
            ForwardServer.address_family = socket.AF_INET6
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=True)


class LocalPortForwardingHandler(SocketServer.BaseRequestHandler):
    host, port, ssh_transport = None, None, None

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip', (self.host, self.port),
                                                   self.request.getpeername())
        except Exception:
            return
        if chan is None:
            return
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
