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


import jarray

from java.io import BufferedReader, InputStreamReader, IOException, \
                    FileOutputStream, BufferedWriter, OutputStreamWriter
from com.trilead.ssh2 import StreamGobbler, SCPClient, Connection, SFTPv3Client, \
                             SFTPv3FileAttributes, SFTPException


class SSHClient(object):

    def __init__(self, host, port=22):
        self.client = Connection(host, port)
        self.client.connect()
        self.shell = None

    def login(self, username, password):
        if not self.client.authenticateWithPassword(username, password):
            raise AssertionError("Authentication failed for user: %s" % username)
        
    def close(self):
        self.client.close()

    def execute_command(self, command, ret_mode):
        sess = self.client.openSession()
        sess.execCommand(command)
        outputs = self._read_outputs(sess, ret_mode)
        sess.close()
        return outputs

    def _read_outputs(self, sess, ret_mode):
        stdoutReader = BufferedReader(InputStreamReader(StreamGobbler(sess.getStdout())))
        stderrReader = BufferedReader(InputStreamReader(StreamGobbler(sess.getStderr())))
        stdout = self._read_from_stream(stdoutReader)
        stderr = self._read_from_stream(stderrReader)
        if ret_mode.lower()=='both':
            return stdout, stderr
        if ret_mode.lower()=='stderr':
            return stderr
        return stdout

    def _read_from_stream(self, streamReader):
        result = ''
        line = streamReader.readLine()
        while line:
            result += line + '\n'
            line = streamReader.readLine()
        return result

    def start_command(self, command):
        self.sess = self.client.openSession()
        self.sess.execCommand(command)

    def read_command_output(self, ret_mode):
        outputs = self._read_outputs(self.sess, ret_mode)
        self.sess.close()
        return outputs

    def open_shell(self):
        self.shell = self.client.openSession()
        self.shell.requestDumbPTY()
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
                
    def put_file(self, source, dest, mode):
        size = 0
        localfile = open(source, 'rb')
        remotefile = self.sftp_client.createFile(dest)
        try:
            tempstats = self.sftp_client.fstat(remotefile)
            tempstats.permissions = mode
            self.sftp_client.fsetstat(remotefile, tempstats)
        except SFTPException:
            pass
        while True:
            data = localfile.read(4096)
            datalen = len(data)
            if datalen == 0:
                break
            self.sftp_client.write(remotefile, size, data, 0, datalen)
            size += datalen
        self.sftp_client.closeFile(remotefile)
        localfile.close()
        
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
