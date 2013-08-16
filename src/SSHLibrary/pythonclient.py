#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

import posixpath

try:
    import paramiko
except ImportError:
    raise ImportError(
            'Importing paramiko SSH module failed.\n'
            'Ensure that paramiko and pycrypto modules are installed.'
            )

from .abstractclient import (AbstractSSHClient, AbstractSFTPClient,
        AbstractCommand, SSHClientException)


# There doesn't seem to be a simpler way to increase banner timeout
def _monkey_patched_start_client(self, event=None):
    self.banner_timeout = 45
    self._orig_start_client(event)


# See http://code.google.com/p/robotframework-sshlibrary/issues/detail?id=55
def _monkey_patched_log(self, level, msg, *args):
    escape = lambda s: s.replace('%', '%%')
    if isinstance(msg, basestring):
        msg = escape(msg)
    else:
        msg = [escape(m) for m in msg]
    return self._orig_log(level, msg, *args)


paramiko.transport.Transport._orig_start_client = \
        paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _monkey_patched_start_client
paramiko.sftp_client.SFTPClient._orig_log = \
        paramiko.sftp_client.SFTPClient._log
paramiko.sftp_client.SFTPClient._log = _monkey_patched_log


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
        self.client.connect(self.host, self.port, username, password,
                            look_for_keys=False)

    def _login_with_public_key(self, username, keyfile, password):
        try:
            self.client.connect(self.host, self.port, username, password,
                                key_filename=keyfile)
        except paramiko.AuthenticationException:
            raise SSHClientException

    def close(self):
        self.client.close()

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
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
            data += self.shell.recv(4096)
        return data

    def _read_char(self):
         data = ''
         if self.shell.recv_ready():
            data = self.shell.recv(1)
         return data

    def _create_sftp_client(self):
        return SFTPClient(self.client)


class SFTPClient(AbstractSFTPClient):

    def _list(self, path):
        return self._client.listdir_attr(path)

    def _get_file_permissions(self, fileinfo):
        return fileinfo.st_mode

    def _create_client(self, ssh_client):
        return ssh_client.open_sftp()

    def _resolve_homedir(self):
        return self._client.normalize('.') + '/'

    def _get_file(self, remotepath, localpath):
        self._client.get(remotepath, localpath)

    def _write_to_remote_file(self, remotefile, data, position):
        remotefile.write(data)

    def _close_remote_file(self, remotefile):
        remotefile.close()

    def _create_missing_remote_path(self, path):
        if path == '.':
            return
        if posixpath.isabs(path):
            self._client.chdir('/')
        else:
            self._client.chdir('.')
        for dirname in path.split('/'):
            cwd = self._client.getcwd()
            if dirname and dirname not in self._client.listdir(cwd):
                self._client.mkdir(dirname)
            self._client.chdir(dirname)

    def _create_remote_file(self, dest, mode):
        remotfile = self._client.file(dest, 'wb')
        remotfile.set_pipelined(True)
        self._client.chmod(dest, mode)
        return remotfile

    def _normalize_path(self, path):
        return self._client.normalize(path)


class RemoteCommand(AbstractCommand):

    def read_outputs(self):
        stdout = self._session.makefile('rb', -1).read().decode(self._encoding)
        stderr = self._session.makefile_stderr('rb', -1).read().decode(
            self._encoding)
        rc = self._session.recv_exit_status()
        self._session.close()
        return stdout, stderr, rc

    def _execute(self):
        self._session.exec_command(self._command)
