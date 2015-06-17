import unittest

from SSHLibrary import SSHClient


class TestClienAPI(unittest.TestCase):

    def test_login_close_and_login_again(self):
        s = SSHClient('localhost', prompt='$ ')
        s.login('test', 'test')
        s.execute_command('ls')
        s.close()
        s.login('test', 'test')
        s.execute_command('ls')

    def test_read_until_regexp_with_prefix(self):
        s = SSHClient('localhost', prompt='$ ')
        s.login('test', 'test')
        s.write('faa')
        s.read_until_regexp_with_prefix(r'foo\sfaa', 'foo ')
        s.close()

if __name__ == "__main__":
    unittest.main()
