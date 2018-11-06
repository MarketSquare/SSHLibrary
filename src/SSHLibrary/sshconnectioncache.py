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

    def get_connection(self, alias_or_index=None):
        if alias_or_index is None:
            if not self:
                self.current.raise_error()
            return self.current
        try:
            index = self._resolve_alias_or_index(alias_or_index)
        except ValueError:
            raise RuntimeError("Non-existing index or alias '%s'."
                               % alias_or_index)
        return next((x for x in self._connections if x.config._config['index'].value == index), None)

    def _resolve_index(self, index):
        try:
            index = int(index)
        except TypeError:
            raise ValueError
        return index
