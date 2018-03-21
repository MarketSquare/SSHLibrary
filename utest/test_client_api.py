from os import environ
import unittest

from SSHLibrary import SSHClient

USERNAME = environ.get('RFSL_USERNAME', 'test')
PASSWORD = environ.get('RFSL_PASSWORD', 'test')

class TestClienAPI(unittest.TestCase):

    def test_login_close_and_login_again(self):
        s = SSHClient('localhost', prompt='$ ')
        s.login(USERNAME, PASSWORD)
        s.execute_command('ls')
        s.close()
        s.login(USERNAME, PASSWORD)
        s.execute_command('ls')

    def test_read_until_regexp_with_prefix(self):
        s = SSHClient('localhost', prompt='$ ')
        s.login(USERNAME, PASSWORD)
        s.write('faa')
        s.read_until_regexp_with_prefix(r'foo\sfaa', 'foo ')
        s.close()

if __name__ == "__main__":
    unittest.main()
