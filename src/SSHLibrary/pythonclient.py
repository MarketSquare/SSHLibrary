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
import time

import paramiko
from robot import utils

from abstractclient import AbstractSSHClient

# There doesn't seem to be a simpler way to increase banner timeout
def _monkey_patched_start_client(self, event=None):
    self.banner_timeout = 45
    self._orig_start_client(event)
    
paramiko.transport.Transport._orig_start_client = paramiko.transport.Transport.start_client
paramiko.transport.Transport.start_client = _monkey_patched_start_client


class SSHClient(AbstractSSHClient):
    
    def __init__(self, host, port=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = host
        self.port = port
        self.channel = None
        
    def login(self, username, password):
        self.client.connect(self.host, self.port, username, password)

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

    def write(self, text, prompt):
        if self.channel is None:
            self.channel = self.client.invoke_shell()
            print '*INFO* Opening new channel'
            print '*INFO* %s' % self.read_until(prompt, 30)
        self.channel.sendall(text)

    def read(self):
        if self.channel is None:
            return ""
        data = ''
        while self.channel.recv_ready():
            data += self.channel.recv(100000)
        return data
    
    def read_until(self, expected, timeout):
        data = ''
        start_time = time.time()
        while time.time() < float(timeout) + start_time :
            if self.channel.recv_ready():
                data += self.channel.recv(1)
            if data.count(expected) > 0:
                return data
        return data

    def _read(self):
        if self.channel.recv_ready():
            return self.channel.recv(1)

    def _create_sftp_client(self):
        self.sftp_client = self.client.open_sftp()
        return self.sftp_client.normalize('.') + '/'
        
    def _create_missing_dest_dirs(self, path):
        if os.path.isabs(path):
            self.sftp_client.chdir('/')
        else:
            self.sftp_client.chdir('.')
        for dirname in path.split('/'):
            if dirname and dirname not in self.sftp_client.listdir(self.sftp_client.getcwd()):
                self._info("Creating missing target directory '%s/%s'" % 
                           (self.sftp_client.getcwd(), dirname))
                self.sftp_client.mkdir(dirname)
            self.sftp_client.chdir(dirname)
        
    def _put_files(self, sourcepaths, destpaths, mode):
        for source, destination in zip(sourcepaths, destpaths):
            self.sftp_client.put(source, destination)
            self.sftp_client.chmod(destination, mode)

    def _get_source_files(self, source):
        path, pattern = os.path.split(source)
        sourcefiles = []
        for filename in self.sftp_client.listdir(path):
            if utils.matches(filename, pattern):
                sourcefiles.append(filename)
        return sourcefiles

    def _get_files(self, sourcepaths, destpaths):
        for source, destination in zip(sourcepaths, destpaths):
            self.sftp_client.get(source, destination)
