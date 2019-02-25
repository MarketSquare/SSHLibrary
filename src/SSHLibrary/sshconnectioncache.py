from robot.utils import ConnectionCache
from itertools import islice
from robot.api import logger


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
        conn_index = connection.config.index - 1
        connection.close()
        if connection.config.alias is not None:
            self.aliases.pop(connection.config.alias)
            for key, value in dict(islice(self.aliases.items(), conn_index, None)).items():
                self.aliases[key] = self.aliases[key] - 1
        self.connections.remove(connection)
        for conn in islice(self.connections, conn_index, None):
            conn.config.update(index=conn.config.get('index').value-1)
        self.current = self._no_current
