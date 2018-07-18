from robot.utils import ConnectionCache


class SSHConnectionCache(ConnectionCache):
    def __init__(self):
        ConnectionCache.__init__(self, no_current_msg='No open connection.')

    @property
    def connections(self):
        return self._connections

    @property
    def aliases(self):
        return self._aliases

    def close_current(self):
        connection = self.current
        connection.close()
        if connection.config.alias is not None:
            self.aliases.pop(connection.config.alias)
        self.connections.remove(connection)
        self.current = self._no_current
