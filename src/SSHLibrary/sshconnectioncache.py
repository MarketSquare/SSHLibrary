from robot.utils import ConnectionCache
from itertools import islice


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
        conn_index = self.current_index
        connection.close()
        if connection.config.alias is not None:
            self.aliases.pop(connection.config.alias)
            for key in islice(self.aliases, conn_index - 1, None):
                self.aliases[key] = self.aliases[key] - 1
        self.connections.remove(connection)
        for conn in islice(self.connections, conn_index - 1, None):
            conn.config.update(index=conn.config.get('index').value-1)
        self.current = self._no_current
