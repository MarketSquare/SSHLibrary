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

import jarray
from java.io import (File, BufferedReader, InputStreamReader, IOException,
                     FileOutputStream)
try:
    from com.trilead.ssh2 import (StreamGobbler, Connection, SFTPv3Client,
            SFTPException)
except ImportError:
    raise ImportError('Importing Trilead SSH classes failed. '
                      'Make sure you have the Trilead jar file in CLASSPATH.')

from .abstractclient import (AbstractSSHClient, AbstractSFTPClient,
        AbstractCommand, SSHClientException)


class JavaSSHClient(AbstractSSHClient):

    @staticmethod
    def enable_logging(logfile):
        return False

    def _create_client(self):
        client = Connection(self.host, self.port)
        client.connect()
        return client

    def _login(self, username, password):
        if not self.client.authenticateWithPassword(username, password):
            raise SSHClientException

    def _login_with_public_key(self, username, keyfile, password):
        try:
            success = self.client.authenticateWithPublicKey(
                            username, File(keyfile), password)
            if not success:
                raise SSHClientException
        except IOError:
            # IOError is raised also when key file is invalid
            raise SSHClientException

    def close(self):
        self.client.close()

    def _start_command(self, command):
        cmd = RemoteCommand(command, self.config.encoding)
        cmd.run_in(self.client.openSession())
        return cmd

    def open_shell(self):
        self.shell = self.client.openSession()
        self.shell.requestPTY(self.config.term_type, self.config.width,
                self.config.height, 0, 0, None)
        self.shell.startShell()
        self._writer = self.shell.getStdin()
        self._stdout = self.shell.getStdout()

    def _write(self, text):
        self._writer.write(text)
        self._writer.flush()

    def _read(self):
         data = ''
         if self._stdout.available():
             buf = jarray.zeros(self._stdout.available(), 'b')
             self._stdout.read(buf)
             data = ''.join([chr(c) for c in buf])
         return data

    def _read_char(self):
         data = ''
         if self._stdout.available():
             data = chr(self._stdout.read())
         return data

    def _create_sftp_client(self):
        return SFTPClient(self.client)


class SFTPClient(AbstractSFTPClient):

    def _create_client(self, ssh_client):
        return SFTPv3Client(ssh_client)

    def _resolve_homedir(self):
        return self._client.canonicalPath('.') + '/'

    def _create_missing_remote_path(self, path):
        if path.startswith('/'):
            curdir = '/'
        else:
            curdir = self._client.canonicalPath('.')
        for dirname in path.split('/'):
            if dirname:
                curdir = '%s/%s' % (curdir, dirname)
            try:
                self._client.stat(curdir)
            except IOException:
                self._client.mkdir(curdir, 0744)

    def _create_remote_file(self, dest, mode):
        remotefile = self._client.createFile(dest)
        try:
            tempstats = self._client.fstat(remotefile)
            tempstats.permissions = mode
            self._client.fsetstat(remotefile, tempstats)
        except SFTPException:
            pass
        return remotefile

    def _write_to_remote_file(self, remotefile, data, position):
        self._client.write(remotefile, position, data, 0, len(data))

    def _close_remote_file(self, remotefile):
        self._client.closeFile(remotefile)

    def _listfiles(self, path):
        return [finfo.filename for finfo in self._client.ls(path)
                if finfo.attributes.getOctalPermissions().startswith('0100')]

    def _get_file(self, source, dest):
        localfile = FileOutputStream(dest)
        tempstats = self._client.stat(source)
        remotefilesize = tempstats.size
        remotefile = self._client.openFileRO(source)
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


class RemoteCommand(AbstractCommand):

    def read_outputs(self):
        stdout = self._read_from_stream(self._session.getStdout())
        stderr = self._read_from_stream(self._session.getStderr())
        rc = self._session.getExitStatus()
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
