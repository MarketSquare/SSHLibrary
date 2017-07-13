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

from robot.utils import is_string, unic, is_unicode

import time
import ntpath

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
def _custom_start_client(self, *args, **kwargs):
    self.banner_timeout = 45
    self._orig_start_client(*args, **kwargs)

paramiko.transport.Transport._orig_start_client = \
    paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _custom_start_client


# See http://code.google.com/p/robotframework-sshlibrary/issues/detail?id=55
def _custom_log(self, level, msg, *args):
    escape = lambda s: s.replace('%', '%%')
    if is_string(msg):
        msg = escape(msg)
    else:
        msg = [escape(m) for m in msg]
    return self._orig_log(level, msg, *args)

paramiko.sftp_client.SFTPClient._orig_log = paramiko.sftp_client.SFTPClient._log
paramiko.sftp_client.SFTPClient._log = _custom_log


class PythonSSHClient(AbstractSSHClient):

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    @staticmethod
    def enable_logging(path):
        paramiko.util.log_to_file(path)
        return True

    def _login(self, username, password, look_for_keys=False):
        try:
            self.client.connect(self.config.host, self.config.port, username,
                                password, look_for_keys=look_for_keys,
                                allow_agent=look_for_keys,
                                timeout=float(self.config.timeout))
        except paramiko.AuthenticationException:
            raise SSHClientException

    def _login_with_public_key(self, username, key_file, password):
        try:
            self.client.connect(self.config.host, self.config.port, username,
                                password, key_filename=key_file,
                                allow_agent=False, timeout=float(self.config.timeout))
        except paramiko.AuthenticationException:
            raise SSHClientException

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
        transport = self.client.get_transport()
        if not transport:
            raise AssertionError("Connection not open")
        new_shell = transport.open_session()
        cmd.run_in(new_shell)
        return cmd

    def _create_sftp_client(self):
        return SFTPClient(self.client, self.config.encoding)

    def _create_shell(self):
        return Shell(self.client, self.config.term_type,
                     self.config.width, self.config.height)


class Shell(AbstractShell):

    def __init__(self, client, term_type, term_width, term_height):
        self._shell = client.invoke_shell(term_type, term_width, term_height)

    def read(self):
        data = bytes()
        while self._output_available():
            data += self._shell.recv(4096)
        return data

    def read_byte(self):
         if self._output_available():
            return self._shell.recv(1)
         return bytes()

    def _output_available(self):
        return self._shell.recv_ready()

    def write(self, text):
        self._shell.sendall(text)


class SFTPClient(AbstractSFTPClient):

    def __init__(self, ssh_client, encoding):
        self._client = ssh_client.open_sftp()
        super(SFTPClient, self).__init__(encoding)

    def _list(self, path):
        path = path.encode(self._encoding)
        for item in self._client.listdir_attr(path):
            filename = item.filename
            if not is_string(filename):
                filename = unic(filename)
            yield SFTPFileInfo(filename, item.st_mode)

    def _stat(self, path):
        path = path.encode(self._encoding)
        attributes = self._client.stat(path)
        return SFTPFileInfo('', attributes.st_mode)

    def _create_missing_remote_path(self, path):
        path = path.encode(self._encoding)
        return super(SFTPClient, self)._create_missing_remote_path(path)

    def _create_remote_file(self, destination, mode):
        destination = destination.encode(self._encoding)
        remote_file = self._client.file(destination, 'wb')
        remote_file.set_pipelined(True)
        self._client.chmod(destination, mode)
        return remote_file

    def _write_to_remote_file(self, remote_file, data, position):
        remote_file.write(data)

    def _close_remote_file(self, remote_file):
        remote_file.close()

    def _get_file(self, remote_path, local_path):
        remote_path = remote_path.encode(self._encoding)
        self._client.get(remote_path, local_path)

    def _absolute_path(self, path):
        path = path.encode(self._encoding)
        if not self._is_windows_path(path):
            path = self._client.normalize(path)
        if not is_unicode(path):
            path = path.decode(self._encoding)
        return path

    def _is_windows_path(self, path):
        return bool(ntpath.splitdrive(path)[0])

class RemoteCommand(AbstractCommand):

    def read_outputs(self):
        stderr, stdout = self._receive_stdout_and_stderr()
        rc = self._shell.recv_exit_status()
        self._shell.close()
        return stdout, stderr, rc

    def _receive_stdout_and_stderr(self):
        stdout_filebuffer = self._shell.makefile('rb', -1)
        stderr_filebuffer = self._shell.makefile_stderr('rb', -1)
        stdouts = []
        stderrs = []
        while self._shell_open():
            self._flush_stdout_and_stderr(stderr_filebuffer, stderrs, stdout_filebuffer, stdouts)
            time.sleep(0.01) # lets not be so busy
        stdout = (b''.join(stdouts) + stdout_filebuffer.read()).decode(self._encoding)
        stderr = (b''.join(stderrs) + stderr_filebuffer.read()).decode(self._encoding)
        return stderr, stdout

    def _flush_stdout_and_stderr(self, stderr_filebuffer, stderrs, stdout_filebuffer, stdouts):
        if self._shell.recv_ready():
            stdouts.append(stdout_filebuffer.read(len(self._shell.in_buffer)))
        if self._shell.recv_stderr_ready():
            stderrs.append(stderr_filebuffer.read(len(self._shell.in_stderr_buffer)))

    def _shell_open(self):
        return not (self._shell.closed or
                self._shell.eof_received or
                self._shell.eof_sent or
                not self._shell.active)

    def _execute(self):
        self._shell.exec_command(self._command)
