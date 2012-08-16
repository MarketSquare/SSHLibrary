#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

from core import SSHClient, Command, AuthenticationException


class JavaSSHClient(SSHClient):

    def _create_client(self):
        client = Connection(self.host, self.port)
        client.connect()
        return client

    def login(self, username, password):
        if not self.client.authenticateWithPassword(username, password):
            raise AuthenticationException("Authentication failed for user: %s"
                                          % username)

    def login_with_public_key(self, username, key, password):
        try:
            if not self.client.authenticateWithPublicKey(username, File(key),
                                                         password):
                raise AuthenticationException()
        except IOError:
            # IOError is raised also when key file is invalid
            raise AuthenticationException()

    def close(self):
        self.client.close()

    def _start_command(self, command):
        cmd = RemoteCommand(command)
        cmd.run_in(self.client.openSession())
        return cmd

    def open_shell(self, term_type, width, height):
        self.shell = self.client.openSession()
        self.shell.requestPTY(term_type, width, height, 0, 0, None)
        self.shell.startShell()
        self._writer = self.shell.getStdin()
        self._stdout = self.shell.getStdout()

    def write(self, text):
        self._writer.write(text)
        self._writer.flush()

    def read(self):
        data = ''
        if self._stdout.available():
            buf = jarray.zeros(self._stdout.available(), 'b')
            self._stdout.read(buf)
            data += ''.join([chr(b) for b in buf])
        return data

    def read_char(self):
        if self._stdout.available():
            buf = jarray.zeros(1, 'b')
            self._stdout.read(buf)
            return chr(buf[0])
        return ''

    def create_sftp_client(self):
        self.sftp_client = SFTPv3Client(self.client)
        self.homedir = self.sftp_client.canonicalPath('.') + '/'

    def close_sftp_client(self):
        self.sftp_client.close()

    def create_missing_remote_path(self, path):
        if path.startswith('/'):
            curdir = '/'
        else:
            curdir = self.sftp_client.canonicalPath('.')
        for dirname in path.split('/'):
            if dirname:
                curdir = '%s/%s' % (curdir, dirname)
            try:
                self.sftp_client.stat(curdir)
            except IOException:
                print "*INFO* Creating missing remote directory '%s'" % curdir
                self.sftp_client.mkdir(curdir, 0744)

    def _create_remote_file(self, dest, mode):
        remotefile = self.sftp_client.createFile(dest)
        try:
            tempstats = self.sftp_client.fstat(remotefile)
            tempstats.permissions = mode
            self.sftp_client.fsetstat(remotefile, tempstats)
        except SFTPException:
            pass
        return remotefile

    def _write_to_remote_file(self, remotefile, data, position):
        self.sftp_client.write(remotefile, position, data, 0, len(data))

    def _close_remote_file(self, remotefile):
        self.sftp_client.closeFile(remotefile)

    def listfiles(self, path):
        return [ fileinfo.filename for fileinfo in self.sftp_client.ls(path) if
                 fileinfo.attributes.getOctalPermissions().startswith('0100') ]

    def get_file(self, source, dest):
        localfile = FileOutputStream(dest)
        tempstats = self.sftp_client.stat(source)
        remotefilesize = tempstats.size
        remotefile = self.sftp_client.openFileRO(source)
        size = 0
        arraysize = 4096
        data = jarray.zeros(arraysize, 'b')
        while True:
            moredata = self.sftp_client.read(remotefile, size, data, 0, arraysize)
            datalen = len(data)
            if moredata==-1:
                break
            if remotefilesize-size < arraysize:
                datalen = remotefilesize-size
            localfile.write(data, 0, datalen)
            size += datalen
        self.sftp_client.closeFile(remotefile)
        localfile.flush()
        localfile.close()


class RemoteCommand(Command):

    def _execute(self):
        self._session.execCommand(self._command)

    def _read_outputs(self):
        stdout = self._read_from_stream(self._session.getStdout())
        stderr = self._read_from_stream(self._session.getStderr())
        rc = self._session.getExitStatus()
        self._session.close()
        return stdout, stderr, rc

    def _read_from_stream(self, stream):
        reader = BufferedReader(InputStreamReader(StreamGobbler(stream)))
        result = ''
        line = reader.readLine()
        while line is not None:
            result += line + '\n'
            line = reader.readLine()
        return result
