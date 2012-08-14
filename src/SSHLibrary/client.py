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


class AuthenticationException(RuntimeError):
    pass


class SSHLibraryClient(object):

    def __init__(self, host, port, prompt):
        self.host = host
        self.port = port
        self.prompt = prompt
        self.shell = None
        self.client = self._create_client()

    def execute_command(self, command, want_stdout, want_stderr, want_rc):
        stdout, stderr, rc = self._execute_command(command)
        ret = []
        if want_stdout:
            ret.append(self._process_output(stdout))
        if want_stderr:
            ret.append(self._process_output(stderr))
        if want_rc:
            ret.append(rc)
        if len(ret) == 1:
            return ret[0]
        return ret

    def _process_output(self, text):
        if text.endswith('\n'):
            return text[:-1]
        return text

    def put_file(self, source, dest, mode, newline_char):
        remotefile = self._create_remote_file(dest, mode)
        localfile = open(source, 'rb')
        position = 0
        while True:
            data = localfile.read(4096)
            if not data:
                break
            if newline_char and '\n' in data:
                data = data.replace('\n', newline_char)
            self._write_to_remote_file(remotefile, data, position)
            position += len(data)
        self._close_remote_file(remotefile)
        localfile.close()
