import os
import unittest

from SSHLibrary import abstractclient

abstractclient.AbstractSFTPClient._homedir = "/home"


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


if __name__ == '__main__':
    unittest.main()
