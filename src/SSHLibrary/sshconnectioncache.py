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
        conn_index = connection.config.index + 1
        connection.close()
        if connection.config.alias is not None:
            start_index = self.aliases.get(connection.config.alias) + 1
            self.aliases.pop(connection.config.alias)
            for key, value in self.aliases.items():
                if value == start_index:
                    self.aliases[key] = start_index - 1
                    start_index = start_index + 1
        self.connections.remove(connection)
        for conn in self.connections:
            if conn.config.index == conn_index:
                conn.config.update(index=conn_index-1)
                conn_index = conn_index + 1
        self.current = self._no_current
