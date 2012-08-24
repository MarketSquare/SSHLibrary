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

from config import Configuration, StringEntry, TimeEntry, IntegerEntry


class ClientConfig(Configuration):

    def __init__(self, host, alias, port, timeout, newline, prompt,
                 term_type, width, height, defaults):
        Configuration.__init__(self,
                host=StringEntry(host),
                alias=StringEntry(alias),
                port=IntegerEntry(port or 22),
                timeout=TimeEntry(timeout or defaults.timeout),
                newline=StringEntry(newline or defaults.newline),
                prompt=StringEntry(prompt or defaults.prompt),
                term_type=StringEntry(term_type or 'vt100'),
                width=IntegerEntry(width or 80),
                height=IntegerEntry(height or 24))


class AuthenticationException(RuntimeError):
    pass


class SSHClientException(RuntimeError):
    pass


class Command(object):
    """Base class for remote commands."""

    def __init__(self, command):
        self._command = command
        self._session = None

    def run_in(self, session):
        """Run this command in given SSH session.

        :param session: a session in an already open SSH connection
        """
        self._session = session
        self._execute()

    def read_outputs(self):
        """Return outputs of this command.

        :return: a 3-tuple of stdout, stderr and return code.
        """
        return self._read_outputs()


class SSHClient(object):

    def __init__(self, config):
        self.host = config.host
        self.port = config.port
        self.config = config
        self.shell = None
        self.client = self._create_client()
        self._commands = []

    def execute_command(self, command, return_stdout, return_stderr,
                        return_rc):
        self.start_command(command)
        return self.read_command_output(return_stdout, return_stderr,
                                        return_rc)

    def start_command(self, command):
        self._commands.append(self._start_command(command))

    def read_command_output(self, return_stdout, return_stderr, return_rc):
        stdout, stderr, rc = self._commands.pop().read_outputs()
        ret = []
        if return_stdout:
            ret.append(stdout.rstrip('\n'))
        if return_stderr:
            ret.append(stderr.rstrip('\n'))
        if return_rc:
            ret.append(rc)
        if len(ret) == 1:
            return ret[0]
        return ret

    def write(self, text, add_newline=False):
        """Write `text` in shell session.

        :param str text: the text to be written, must be ASCII.
        :param bool add_newline: if True, a newline will be added to `text`.
        """
        self._ensure_prompt_is_set()
        try:
            text = str(text)
        except UnicodeError:
            raise SSHClientException('Invalid input, only ASCII characters '
                                     'are allowed. Got: %s' % text)
        if add_newline:
            text += self.config.newline
        self._write(text)

    def _ensure_prompt_is_set(self):
        if not self.config.prompt:
            raise SSHClientException('Prompt is not set.')

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
