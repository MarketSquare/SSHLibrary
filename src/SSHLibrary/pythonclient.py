#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import stat
import posixpath
try:
    import paramiko
except ImportError:
    raise ImportError(
            'Importing paramiko SSH module failed.\n'
            'Ensure that paramiko and pycrypto modules are installed.'
            )

from .client import AbstractSSHClient
from .core import Command, SSHClientException


# There doesn't seem to be a simpler way to increase banner timeout
def _monkey_patched_start_client(self, event=None):
    self.banner_timeout = 45
    self._orig_start_client(event)


paramiko.transport.Transport._orig_start_client = \
        paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _monkey_patched_start_client


class PythonSSHClient(AbstractSSHClient):

    @staticmethod
    def enable_logging(path):
        paramiko.util.log_to_file(path)
        return True

    def _create_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    def _login(self, username, password):
        self.client.connect(self.host, self.port, username, password)

    def _login_with_public_key(self, username, keyfile, password):
        try:
            self.client.connect(self.host, self.port, username, password,
                                key_filename=keyfile)
        except paramiko.AuthenticationException:
            raise SSHClientException

    def close(self):
        self.client.close()

    def _start_command(self, command):
        cmd = RemoteCommand(command)
        cmd.run_in(self.client.get_transport().open_session())
        return cmd

    def open_shell(self):
        self.shell = self.client.invoke_shell(self.config.term_type,
                self.config.width, self.config.height)

    def _write(self, text):
        self.shell.sendall(text)

    def _read(self):
        data = ''
        while self.shell.recv_ready():
            data += self.shell.recv(100000)
        return data

    def _read_char(self):
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

    def _create_remote_file(self, dest, mode):
        remotfile = self.sftp_client.file(dest, 'wb')
        remotfile.set_pipelined(True)
        self.sftp_client.chmod(dest, mode)
        return remotfile

    def _write_to_remote_file(self, remotefile, data, position):
        remotefile.write(data)

    def _close_remote_file(self, remotefile):
        remotefile.close()

    def listfiles(self, path):
        return [getattr(fileinfo, 'filename', '?') for fileinfo
                in self.sftp_client.listdir_attr(path)
                if stat.S_ISREG(fileinfo.st_mode) or
                        stat.S_IFMT(fileinfo.st_mode) == 0]

    def get_file(self, source, dest):
        self.sftp_client.get(source, dest)


class RemoteCommand(Command):

    def _execute(self):
        self._session.exec_command(self._command)

    def _read_outputs(self):
        stdout = self._session.makefile('rb', -1).read()
        stderr = self._session.makefile_stderr('rb', -1).read()
        rc = self._session.recv_exit_status()
        self._session.close()
        return stdout, stderr, rc
