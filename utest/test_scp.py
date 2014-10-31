import os
import unittest

from SSHLibrary import abstractclient, SSHClient

abstractclient.AbstractSFTPClient._absolute_path = lambda obj, path: '/home'

class TestRemoteAndLocalPathResolution(unittest.TestCase):

    def test_put_file(self):
        data = [(['foo.txt'], 'foo.txt', ['/home/foo.txt']),
                (['txt.bar'], 'c:/tmp/foo.txt', ['/tmp/foo.txt']),
                (['FOO.TXT'], '.', ['/home/FOO.TXT']),
                (['foo.txt', 'bar.sh', 'BAZ.my'], '/opt/Files/',
                    ['/opt/Files/foo.txt', '/opt/Files/bar.sh',
                     '/opt/Files/BAZ.my']),
                (['myfile'], '\\tmp\\', ['/tmp/myfile'])]
        for src, dest, exp in data:
            client = abstractclient.AbstractSFTPClient()
            client.is_dir = lambda x: False
            remote = client._get_put_file_destinations(src, dest, '/')[0]
            self.assertEquals(remote, exp)

    def test_get_file(self):
        data = [(['foo.txt'], '/home/test/', ['/home/test/foo.txt']),
                (['myf.xyzzy'], '/home/yzzyx.myf', ['/home/yzzyx.myf']),
                (['FOO.sh', 'bar.TXT'], '/home/',
                    ['/home/FOO.sh', '/home/bar.TXT']),
                (['/home/baz.file'], '.',
                    [os.path.join(os.path.abspath(os.curdir), 'baz.file')])]
        for src, dest, exp in data:
            client = abstractclient.AbstractSFTPClient()
            local = client._get_get_file_destinations(src, dest)
            self.assertEquals(local, exp)


class TestSSHClientGetMethod(unittest.TestCase):

    SRC_DIR = '/tmp/src'
    DST_DIR = '/tmp/dst'
    TEST_FILE = '/tmp/src/test_file.txt'

    def setUp(self):
        self._prepare_environment()

    def tearDown(self):
        self._clean_enrvironment()

    def test_get_file_downloads_file_via_second_ssh_session(self):
        client = self._create_ssh_client()
        client.get_file(self.TEST_FILE, self.DST_DIR)
        client.close()
        self._login_client(client)
        client.get_file(self.TEST_FILE, self.DST_DIR)
        client.close()

    def _prepare_environment(self):
        client = self._create_ssh_client()
        self._create_test_dirs(client)
        self._create_test_file(client)
        client.close()

    def _create_ssh_client(self):
        client = SSHClient('localhost', prompt='$ ')
        self._login_client(client)
        return client

    def _login_client(self, client):
        client.login('test', 'test')

    def _create_test_dirs(self, client):
        client.execute_command("mkdir -p %s" % self.SRC_DIR)

    def _create_test_file(self, client):
        client.execute_command("touch %s" % self.TEST_FILE)

    def _remove_test_dirs(self, client):
        client.execute_command("rm -rf %s" % self.SRC_DIR)

    def _clean_enrvironment(self):
        client = self._create_ssh_client()
        self._remove_test_dirs(client)
        client.close()


if __name__ == '__main__':
    unittest.main()
