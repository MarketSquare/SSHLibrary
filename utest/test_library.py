import unittest

from SSHLibrary import SSHLibrary


HOSTNAME = 'localhost'


class TestSSHLibraryConfiguration(unittest.TestCase):

    def test_default_confguration(self):
        self._assert_config(SSHLibrary()._config)

    def test_setting_configruation_values(self):
        cfg = SSHLibrary(newline='CRLF', prompt='$')._config
        self._assert_config(cfg, newline='\r\n', prompt='$')

    def test_set_default_confguarition(self):
        timeout, newline, prompt, level = 1, '\r\n', '>', 'DEBUG'
        lib = SSHLibrary()
        lib.set_default_configuration(timeout=timeout,
                                      newline=newline,
                                      prompt=prompt,
                                      loglevel=level)
        self._assert_config(lib._config, timeout, newline, prompt, level)

    def _assert_config(self, cfg, timeout=3, newline='\n', prompt=None,
                       loglevel='INFO'):
        self.assertEquals(cfg.timeout, timeout)
        self.assertEquals(cfg.newline, newline)
        self.assertEquals(cfg.prompt, prompt)
        self.assertEquals(cfg.loglevel, loglevel)


class TestSSHClientConfiguration(unittest.TestCase):

    def test_default_client_configuration(self):
        lib = SSHLibrary()
        lib.open_connection(HOSTNAME)
        self._assert_config(lib.current.config)

    def test_overriding_client_configuration(self):
        lib = SSHLibrary(timeout=4)
        lib.open_connection(HOSTNAME, timeout=5)
        self._assert_config(lib.current.config, timeout=5)

    def test_set_client_confguration(self):
        timeout, term_type = 23, 'ansi'
        lib = SSHLibrary()
        lib.open_connection(HOSTNAME)
        lib.set_client_configuration(timeout=timeout,
                                     term_type=term_type)
        self._assert_config(lib.current.config, timeout=timeout,
                            term_type=term_type)

    def _assert_config(self, cfg, host=HOSTNAME, timeout=3, newline='\n',
                       prompt=None, port=22, term_type='vt100'):
        self.assertEquals(cfg.host, host)
        self.assertEquals(cfg.timeout, timeout)
        self.assertEquals(cfg.newline, newline)
        self.assertEquals(cfg.prompt, prompt)
        self.assertEquals(cfg.term_type, term_type)
        self.assertEquals(cfg.port, port)


if __name__ == '__main__':
    unittest.main()
