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

import time

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

    def read(self):
        """Read and return currently available output."""
        return self._read()

    def read_char(self):
        """Read and return a single character from current session."""
        return self._read_char()

    def read_until(self, expected):
        """Read and return from the output until expected.

        :param str expected: text to look for in the output
        :raises SSHClientException: if expected is not found in output when
            timeout expires.

        timeout is defined with :py:methc:`open_connection()`
        """
        return self._read_until(lambda s: expected in s, expected)

    def read_until_newline(self):
        """Read and return from the output up to the first newline character.

        :raises SSHClientException: if newline is not found in output when
            timeout expires.

        timeout is defined with :py:methc:`open_connection()`
        """
        return self.read_until(self.config.newline)

    def read_until_prompt(self):
        """Read and return from the output until prompt.

        :raises SSHClientException: if prompt is not set or it is not found
            in output when timeout expires.

        prompt and timeout are defined with :py:methc:`open_connection()`
        """
        self._ensure_prompt_is_set()
        return self.read_until(self.config.prompt)

    def read_until_regexp(self, regexp):
        """Read and return from the output until regexp matches.

        :param regexp: a compiled regexp obect used for matching
        :raises SSHClientException: if match is not found in output when
            timeout expires.

        timeout is defined with :py:methc:`open_connection()`
        """
        return self._read_until(lambda s: regexp.search(s), regexp.pattern)

    def write_until_expected(self, text, expected, timeout, interval):
        """Write text until expected output appears or timeout expires.

        :param str text: Text to be written using #write_bare().
        :param str expected: Text to look for in the output.
        :param int timeout: The timeout during which `expected` must appear
            in the output, in seconds.
        :param int interval: Time to wait between repeated writings'
        """
        timeout = TimeEntry(timeout)
        starttime = time.time()
        while time.time() - starttime < timeout.value:
            self.write(text)
            try:
                return self._read_until(lambda s: expected in s,
                                        expected, timeout=interval)
            except SSHClientException:
                pass
        raise SSHClientException("No match found for '%s' in %s."
                                 % (expected, timeout))

    def _read_until(self, matcher, expected, timeout=None):
        ret = ''
        timeout = TimeEntry(timeout) if timeout else self.config.get('timeout')
        start_time = time.time()
        while time.time() < float(timeout.value) + start_time:
            ret += self._read_char()
            if matcher(ret):
                return ret
        raise SSHClientException("No match found for '%s' in %s\nOutput:\n%s"
                                 % (expected, timeout, ret))

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
