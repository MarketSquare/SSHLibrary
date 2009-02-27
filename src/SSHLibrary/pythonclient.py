#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import os
import stat
import posixpath

from robot.errors import DataError
try:
    import paramiko
except ImportError:
    raise ImportError('Importing paramiko SSH module or its dependencies failed. '
                      'Make sure you have the required modules installed.')

# There doesn't seem to be a simpler way to increase banner timeout
def _monkey_patched_start_client(self, event=None):
    self.banner_timeout = 45
    self._orig_start_client(event)
    
paramiko.transport.Transport._orig_start_client = paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _monkey_patched_start_client


class SSHClient(object):

    enable_ssh_logging = staticmethod(lambda path: paramiko.util.log_to_file(path))
    
    def __init__(self, host, port=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = host
        self.port = port
        self.shell = None
        
    def login(self, username, password):
        self.client.connect(self.host, self.port, username, password)
        
    def login_with_public_key(self, username, keyfile, password):
        try:
            self.client.connect(self.host, self.port, username, password, 
                                key_filename=keyfile)
        except paramiko.AuthenticationException:
            raise DataError()

    def close(self):
        self.client.close()

    def execute_command(self, command, ret_mode):
        _, stdout, stderr = self.client.exec_command(command)
        return self._read_command_output(stdout, stderr, ret_mode)

    def start_command(self, command):
        _, self.stdout, self.stderr = self.client.exec_command(command)

    def read_command_output(self, ret_mode):
        return self._read_command_output(self.stdout, self.stderr, ret_mode)

    def _read_command_output(self, stdout, stderr, ret_mode):
        if ret_mode.lower() == 'both':
            return stdout.read(), stderr.read()
        if ret_mode.lower() == 'stderr':
            return stderr.read()
        return stdout.read()
    
    def open_shell(self):
        self.shell = self.client.invoke_shell()
        
    def write(self, text):
        self.shell.sendall(text)

    def read(self):
        data = ''
        while self.shell.recv_ready():
            data += self.shell.recv(100000)
        return data

    def read_char(self):
        if self.shell.recv_ready():
            return self.shell.recv(1)
        return ''

    def create_sftp_client(self):
        self.sftp_client = self.client.open_sftp()
        self.homedir = self.sftp_client.normalize('.') + '/'
        
    def close_sftp_client(self):
        self.sftp_client.close()
        
    def create_missing_remote_path(self, path):
        if path == '.':
            return
        if posixpath.isabs(path):
            self.sftp_client.chdir('/')
        else:
            self.sftp_client.chdir('.')
        for dirname in path.split('/'):
            if dirname and dirname not in self.sftp_client.listdir(self.sftp_client.getcwd()):
                print "*INFO* Creating missing remote directory '%s'" % dirname
                self.sftp_client.mkdir(dirname)
            self.sftp_client.chdir(dirname)
        
    def put_file(self, source, dest, mode):
        self.sftp_client.put(source, dest)
        self.sftp_client.chmod(dest, mode)
        
    def listfiles(self, path):
        return[ getattr(fileinfo, 'filename', '?') for fileinfo 
                in self.sftp_client.listdir_attr(path)
                if stat.S_ISREG(fileinfo.st_mode) or stat.S_IFMT(fileinfo.st_mode) == 0 ]

    def get_file(self, source, dest):
        self.sftp_client.get(source, dest)
