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
                             SSHClientException)


class JavaSSHClient(AbstractSSHClient):

    def __init__(self, *args):
        super(JavaSSHClient, self).__init__(*args)
        self.client = Connection(self.config.host, self.config.port)
        self.client.connect()

    @staticmethod
    def enable_logging(logfile):
        return False

    def _login(self, username, password):
        if not self.client.authenticateWithPassword(username, password):
            raise SSHClientException

    def _login_with_public_key(self, username, keyfile, password):
        try:
            success = self.client.authenticateWithPublicKey(username,
                                                            File(keyfile),
                                                            password)
            if not success:
                raise SSHClientException
        except IOError:
            # IOError is raised also when the keyfile is invalid
            raise SSHClientException

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
        cmd.run_in(self.client.openSession())
        return cmd

    def _create_sftp_client(self):
        return SFTPClient(self.client)

    def _create_shell(self):
        return Shell(self.client, self.config.term_type,
                     self.config.width, self.config.height)


class Shell(AbstractShell):

    def __init__(self, client, term_type, term_width, term_height):
        shell = client.openSession()
        shell.requestPTY(term_type,
                               term_width,
                               term_height,
                               0, 0, None)
        shell.startShell()
        self._stdout = shell.getStdout()
        self._stdin = shell.getStdin()

    def read(self):
        data = ''
        if self._output_available():
            read_bytes = jarray.zeros(self._output_available(), 'b')
            self._stdout.read(read_bytes)
            data = ''.join([chr(b & 0xFF) for b in read_bytes])
        return data

    def read_byte(self):
         data = ''
         if self._output_available():
             data = chr(self._stdout.read())
         return data

    def _output_available(self):
        return self._stdout.available()

    def write(self, text):
        self._stdin.write(text)
        self._stdin.flush()


class SFTPClient(AbstractSFTPClient):

    def __init__(self, ssh_client):
        self._client = SFTPv3Client(ssh_client)
        super(SFTPClient, self).__init__()

    def _list(self, path):
        return self._client.ls(path)

    def _get_permissions(self, fileinfo):
        if isinstance(fileinfo, SFTPv3DirectoryEntry):
            return fileinfo.attributes.permissions
        else:
            return fileinfo.permissions

    def _create_remote_file(self, dest, mode):
        remote_file = self._client.createFile(dest)
        try:
            tempstats = self._client.fstat(remote_file)
            tempstats.permissions = mode
            self._client.fsetstat(remote_file, tempstats)
        except SFTPException:
            pass
        return remote_file

    def _write_to_remote_file(self, remotefile, data, position):
        self._client.write(remotefile, position, data, 0, len(data))

    def _close_remote_file(self, remotefile):
        self._client.closeFile(remotefile)

    def _get_file(self, remotepath, localpath):
        localfile = FileOutputStream(localpath)
        tempstats = self._client.stat(remotepath)
        remotefilesize = tempstats.size
        remotefile = self._client.openFileRO(remotepath)
        size = 0
        arraysize = 4096
        data = jarray.zeros(arraysize, 'b')
        while True:
            moredata = self._client.read(remotefile, size, data, 0,
                                             arraysize)
            datalen = len(data)
            if moredata == -1:
                break
            if remotefilesize - size < arraysize:
                datalen = remotefilesize - size
            localfile.write(data, 0, datalen)
            size += datalen
        self._client.closeFile(remotefile)
        localfile.flush()
        localfile.close()

    def _absolute_path(self, path):
        return self._client.canonicalPath(path)


class RemoteCommand(AbstractCommand):

    def read_outputs(self):
        stdout = self._read_from_stream(self._session.getStdout())
        stderr = self._read_from_stream(self._session.getStderr())
        rc = self._session.getExitStatus() or 0
        self._session.close()
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
        self._session.execCommand(self._command)
