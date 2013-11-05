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

try:
    import paramiko
except ImportError:
    raise ImportError(
        'Importing Paramiko library failed. '
        'Make sure you have Paramiko installed.'
    )

from .abstractclient import (AbstractShell, AbstractSFTPClient,
                             AbstractSSHClient, AbstractCommand,
                             SSHClientException, SFTPFileInfo)


# There doesn't seem to be a simpler way to increase banner timeout
def _custom_start_client(self, event=None):
    self.banner_timeout = 45
    self._orig_start_client(event)

paramiko.transport.Transport._orig_start_client = \
    paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _custom_start_client

# See http://code.google.com/p/robotframework-sshlibrary/issues/detail?id=55
def _custom_log(self, level, msg, *args):
    escape = lambda s: s.replace('%', '%%')
    if isinstance(msg, basestring):
        msg = escape(msg)
    else:
        msg = [escape(m) for m in msg]
    return self._orig_log(level, msg, *args)

paramiko.sftp_client.SFTPClient._orig_log = paramiko.sftp_client.SFTPClient._log
paramiko.sftp_client.SFTPClient._log = _custom_log


class PythonSSHClient(AbstractSSHClient):

    def __init__(self, *args):
        super(PythonSSHClient, self).__init__(*args)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @staticmethod
    def enable_logging(path):
        paramiko.util.log_to_file(path)
        return True

    def _login(self, username, password):
        self.client.connect(self.config.host, self.config.port, username,
                            password, look_for_keys=False)

    def _login_with_public_key(self, username, keyfile, password):
        try:
            self.client.connect(self.config.host, self.config.port, username,
                                password, key_filename=keyfile)
        except paramiko.AuthenticationException:
            raise SSHClientException

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
        cmd.run_in(self.client.get_transport().open_session())
        return cmd

    def _create_sftp_client(self):
        return SFTPClient(self.client)

    def _create_shell(self):
        return Shell(self.client, self.config.term_type,
                     self.config.width, self.config.height)


class Shell(AbstractShell):

    def __init__(self, client, term_type, term_width, term_height):
        self._shell = client.invoke_shell(term_type, term_width, term_height)

    def read(self):
        data = ''
        while self._output_available():
            data += self._shell.recv(4096)
        return data

    def read_byte(self):
         if self._output_available():
            return self._shell.recv(1)
         return ''

    def _output_available(self):
        return self._shell.recv_ready()

    def write(self, text):
        self._shell.sendall(text)


class SFTPClient(AbstractSFTPClient):

    def __init__(self, ssh_client):
        self._client = ssh_client.open_sftp()
        super(SFTPClient, self).__init__()

    def _list(self, path):
        return [SFTPFileInfo(item.filename, item.st_mode)
                for item in self._client.listdir_attr(path)]

    def _stat(self, path):
        attributes = self._client.stat(path)
        return SFTPFileInfo('', attributes.st_mode)

    def _create_remote_file(self, dest, mode):
        remote_file = self._client.file(dest, 'wb')
        remote_file.set_pipelined(True)
        self._client.chmod(dest, mode)
        return remote_file

    def _write_to_remote_file(self, remotefile, data, position):
        remotefile.write(data)

    def _close_remote_file(self, remotefile):
        remotefile.close()

    def _get_file(self, remotepath, localpath):
        self._client.get(remotepath, localpath)

    def _absolute_path(self, path):
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
