import unittest
import os

from SSHLibrary.abstractclient import AbstractSSHClient


class _MockClient(AbstractSSHClient):
    
    def __init__(self):
        self.putfile_record = []
        self.getfile_record = []
        self.homedir = '/home'

    def _create_sftp_client(self):
        pass
        
    def _close_sftp_client(self):
        pass

    def _create_missing_dest_dirs(self, dest):
        pass
    
    def _create_missing_local_dirs(self, dest, is_dir):
        pass
    
    def _get_put_file_sources(self, src):
        return src
    
    def _get_get_file_sources(self, src):
        return src
    
    def _put_file(self, src, dest, mode):
        self.putfile_record.append(dest)
        
    def _get_file(self, src, dest):
        self.getfile_record.append(dest)
    
    def _info(self, msg, level=None):
        pass
    

class TestClient(unittest.TestCase):
    
    def setUp(self):
        self._client = _MockClient()
    
    def test_put_file(self):
        data = [ (['foo.txt'], 'foo.txt', ['/home/foo.txt']), 
                 (['txt.bar'], '/tmp/foo.txt', ['/tmp/foo.txt']),
                 (['FOO.TXT'], '.', ['/home/FOO.TXT']),
                 (['foo.txt', 'bar.sh', 'BAZ.my'], '/opt/Files/', 
                  ['/opt/Files/foo.txt', '/opt/Files/bar.sh', '/opt/Files/BAZ.my']),
                 (['myfile'], '\\tmp\\', ['/tmp/myfile']) ]
        for src, dest, exp in data:
            client = _MockClient() 
            client.put_file(src, dest, 0744)
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
            client.get_file(src, dest)
            self.assertEquals(client.getfile_record, exp)


if __name__ == '__main__':
    unittest.main()
