import unittest

from SSHLibrary.config import (Configuration, ConfigurationException,
                               IntegerEntry, LogLevelEntry, NewlineEntry,
                               StringEntry, TimeEntry)

STRING_VALUE = 'some value'
INTEGER_STRING = '42'
INTEGER_VALUE = 42
TIME_STRING = '3 minutes 25 seconds'
TIME = 205


class TestConfigurationEntries(unittest.TestCase):

    def test_creating_with_initial_value(self):
        entry = StringEntry(initial=STRING_VALUE)
        self._assert_entry(entry, STRING_VALUE)

    def test_setting_value(self):
        entry = StringEntry()
        entry.set(STRING_VALUE)
        self._assert_entry(entry, STRING_VALUE)

    def test_integer_entry(self):
        entry = IntegerEntry(INTEGER_STRING)
        self._assert_entry(entry, INTEGER_VALUE)

    def test_time_entry(self):
        entry = TimeEntry(TIME_STRING)
        self._assert_entry(entry, 205)

    def test_log_level_entry(self):
        entry = LogLevelEntry('debug')
        self._assert_entry(entry, 'DEBUG')

    def test_newline_entry(self):
        entry = NewlineEntry('crlf')
        self._assert_entry(entry, '\r\n')

    def _assert_entry(self, entry, expected_value):
        self.assertEquals(entry.value, expected_value)


class TestConfiguration(unittest.TestCase):

    def test_creating_configuration(self):
        cfg = Configuration(name=StringEntry(STRING_VALUE))
        self.assertEquals(cfg.name, STRING_VALUE)

    def test_updating_configuration_values(self):
        cfg = Configuration(entry=StringEntry('other value'))
        cfg.update(entry=STRING_VALUE)
        self.assertEquals(cfg.entry, STRING_VALUE)

    def test_missing_config_item(self):
        self.assertRaises(ConfigurationException,
                lambda: Configuration().missing)


if __name__ == '__main__':
    unittest.main()
