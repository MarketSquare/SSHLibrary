from robot import utils


class ConfigurationException(Exception):
    """Raised when creating, updating or accessing a Configuration entry fails."""
    pass


class Configuration(object):
    """A simple configuration class.

    Configuration is defined with keyword arguments, in which the value must
    be an instance of :py:class:`Entry`. Different subclasses of `Entry` can
    be used to handle common types and conversions.

    Example::

        cfg = Configuration(name=StringEntry('initial'),
                            age=IntegerEntry('42'))
        assert cfg.name == initial
        assert cfg.age == 42
        cfg.update(name='John Doe')
        assert cfg.name == 'John Doe'
    """

    def __init__(self, **config):
        self._config = config

    def update(self, **config):
        """Update configuration entries. See `__init__` for an example."""
        for name in config:
            self._config[name].set(config[name])

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name].value
        msg = "Configuration parameter '%s' is not defined" % name
        raise ConfigurationException(msg)


class Entry(object):
    """A base class for values stored in :py:class:`Configuration`.

        :param:`initial` the initial value of this entry.
    """

    def __init__(self, initial=None):
        self._value = self._create_value(initial)

    @property
    def value(self):
        return self._value

    def set(self, value):
        self._value = self._parse_value(value)

    def _create_value(self, value):
        if value is None:
            return None
        return self._parse_value(value)


class StringEntry(Entry):
    """String value to be stored in :py:class:`Configuration`."""
    def _parse_value(self, value):
        return value


class IntegerEntry(Entry):
    """Integer value to be stored in stored in :py:class:`Configuration`.

    Given value is converted to string using `int()`.
    """
    def _parse_value(self, value):
        return int(value)


class TimeEntry(Entry):
    """Time string to be stored in :py:class:`Configuration`.

    Given time string will be converted to seconds using
    :py:func:`robot.utils.timestr_to_secs`.
    """
    def _parse_value(self, value):
        return utils.timestr_to_secs(value) if value else None


class LogLevelEntry(Entry):
    """Log level to be stored in :py:class:`Configuration`.

    Given string must be on of 'TRACE', 'DEBUG', 'INFO' or 'WARN', case
    insensitively.
    """
    def _parse_value(self, value):
        return value.upper()


class NewlineEntry(Entry):
    """New line sequence to be stored in :py:class:`Configuration`.

    Following conversion are performed on the given string:
        * 'LF' -> '\n'
        * 'CR' -> '\r'
    """
    def _parse_value(self, value):
        return value.upper().replace('LF', '\n').replace('CR', '\r')
