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
    from com.trilead.ssh2 import (Connection, SFTPException, SFTPv3Client,
                                  SFTPv3DirectoryEntry, StreamGobbler)
except ImportError:
    raise ImportError(
        'Importing Trilead SSH library failed. '
        'Make sure you have the Trilead JAR distribution in your CLASSPATH.'
    )
import jarray
from java.io import (BufferedReader, File, FileOutputStream, InputStreamReader,
                     IOException)

from .abstractclient import (AbstractShell, AbstractSSHClient,
                             AbstractSFTPClient, AbstractCommand,
                             SSHClientException, SFTPFileInfo)


class JavaSSHClient(AbstractSSHClient):

    def _get_client(self):
        client = Connection(self.config.host, self.config.port)
        timeout = int(float(self.config.timeout)*1000)
        client.connect(None, timeout, timeout)
        return client

    @staticmethod
    def enable_logging(logfile):
        return False

    def _login(self, username, password, look_for_keys='ignored'):
        if not self.client.authenticateWithPassword(username, password):
            raise SSHClientException

    def _login_with_public_key(self, username, key_file, password):
        try:
            success = self.client.authenticateWithPublicKey(username,
                                                            File(key_file),
                                                            password)
            if not success:
                raise SSHClientException
        except IOError:
            # IOError is raised also when the keyfile is invalid
            raise SSHClientException

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
        new_shell = self.client.openSession()
        cmd.run_in(new_shell)
        return cmd

    def _create_sftp_client(self):
        return SFTPClient(self.client, self.config.encoding)

    def _create_shell(self):
        return Shell(self.client, self.config.term_type,
                     self.config.width, self.config.height)


class Shell(AbstractShell):

    def __init__(self, client, term_type, term_width, term_height):
        shell = client.openSession()
        shell.requestPTY(term_type, term_width, term_height, 0, 0, None)
        shell.startShell()
        self._stdout = shell.getStdout()
        self._stdin = shell.getStdin()

    def read(self):
        if self._output_available():
            read_bytes = jarray.zeros(self._output_available(), 'b')
            self._stdout.read(read_bytes)
            return ''.join(chr(b & 0xFF) for b in read_bytes)
        return ''

    def read_byte(self):
         if self._output_available():
             return chr(self._stdout.read())
         return bytes()

    def _output_available(self):
        return self._stdout.available()

    def write(self, text):
        self._stdin.write(text)
        self._stdin.flush()


class SFTPClient(AbstractSFTPClient):

    def __init__(self, ssh_client, encoding):
        self._client = SFTPv3Client(ssh_client)
        self._client.setCharset(encoding)
        super(SFTPClient, self).__init__(encoding)

    def _list(self, path):
        for item in self._client.ls(path):
            if item.filename not in ('.', '..'):
                yield SFTPFileInfo(item.filename, item.attributes.permissions)

    def _stat(self, path):
        attributes = self._client.stat(path)
        return SFTPFileInfo('', attributes.permissions)

    def _create_remote_file(self, destination, mode):
        remote_file = self._client.createFile(destination)
        try:
            file_stat = self._client.fstat(remote_file)
            file_stat.permissions = mode
            self._client.fsetstat(remote_file, file_stat)
        except SFTPException:
            pass
        return remote_file

    def _write_to_remote_file(self, remote_file, data, position):
        self._client.write(remote_file, position, data, 0, len(data))

    def _close_remote_file(self, remote_file):
        self._client.closeFile(remote_file)

    def _get_file(self, remote_path, local_path):
        local_file = FileOutputStream(local_path)
        remote_file_size = self._client.stat(remote_path).size
        remote_file = self._client.openFileRO(remote_path)
        array_size_bytes = 4096
        data = jarray.zeros(array_size_bytes, 'b')
        offset = 0
        while True:
            read_bytes = self._client.read(remote_file, offset, data, 0,
                                           array_size_bytes)
            data_length = len(data)
            if read_bytes == -1:
                break
            if remote_file_size - offset < array_size_bytes:
                data_length = remote_file_size - offset
            local_file.write(data, 0, data_length)
            offset += data_length
        self._client.closeFile(remote_file)
        local_file.flush()
        local_file.close()

    def _absolute_path(self, path):
        return self._client.canonicalPath(path)


class RemoteCommand(AbstractCommand):

    def read_outputs(self):
        stdout = self._read_from_stream(self._shell.getStdout())
        stderr = self._read_from_stream(self._shell.getStderr())
        rc = self._shell.getExitStatus() or 0
        self._shell.close()
        return stdout, stderr, rc

    def _read_from_stream(self, stream):
        reader = BufferedReader(InputStreamReader(StreamGobbler(stream),
                                                  self._encoding))
        result = ''
        line = reader.readLine()
        while line is not None:
            result += line + '\n'
            line = reader.readLine()
        return result

    def _execute(self):
        self._shell.execCommand(self._command)
