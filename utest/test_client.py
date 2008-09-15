import unittest
import os

from SSHLibrary import SSHLibrary


class _MockClient(object):
    
    def __init__(self):
        self.putfile_record = []
        self.getfile_record = []
        self.homedir = '/home'

    def put_file(self, src, dest, mode):
        self.putfile_record.append(dest)
        
    def get_file(self, src, dest):
        self.getfile_record.append(dest)

    create_sftp_client = close_sftp_client = lambda self: None
    create_missing_remote_path = lambda self, x: None
    

class MySSHLibrary(SSHLibrary):
    _create_missing_local_dirs = lambda self, x, y: None
    _get_put_file_sources = _info = lambda self, x: x
    _get_get_file_sources = lambda self, x: x
    

class TestClient(unittest.TestCase):
    
    def test_put_file(self):
        data = [ (['foo.txt'], 'foo.txt', ['/home/foo.txt']), 
                 (['txt.bar'], 'c:/tmp/foo.txt', ['/tmp/foo.txt']),
                 (['FOO.TXT'], '.', ['/home/FOO.TXT']),
                 (['foo.txt', 'bar.sh', 'BAZ.my'], '/opt/Files/', 
                  ['/opt/Files/foo.txt', '/opt/Files/bar.sh', '/opt/Files/BAZ.my']),
                 (['myfile'], '\\tmp\\', ['/tmp/myfile']) ]
        for src, dest, exp in data:
            client = _MockClient()
            lib = MySSHLibrary()
            lib._client = client
            lib.put_file(src, dest, '0744')
            self.assertEquals(client.putfile_record, exp)
    
    def test_get_file(self):
        data = [ (['foo.txt'], '/home/test/', ['/home/test/foo.txt']),
                 (['myf.xyzzy'], '/home/yzzyx.myf', ['/home/yzzyx.myf']),
                 (['FOO.sh', 'bar.TXT'], '/home/', ['/home/FOO.sh', '/home/bar.TXT']),
                 (['/home/baz.file'], '.', [os.path.join(os.path.abspath(os.curdir), 'baz.file')]),
              #  (['\\myfile'], '/home/', ['/home/myfile'])
                 ]
        for src, dest, exp in data:
            client = _MockClient()
            lib = MySSHLibrary()
            lib._client = client
            lib.get_file(src, dest)
            self.assertEquals(client.getfile_record, exp)


if __name__ == '__main__':
    unittest.main()
