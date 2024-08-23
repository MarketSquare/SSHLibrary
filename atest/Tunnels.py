import socket
from robot.api.deco import library, keyword


@library
class Tunnels:

    @keyword
    def dummy_connect(self, local_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", int(local_port)))
        s.close()
