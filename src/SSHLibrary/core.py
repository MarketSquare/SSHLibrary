#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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


from config import (Configuration, StringEntry, TimeEntry, IntegerEntry,
        NewlineEntry, LogLevelEntry)


class SSHClientException(RuntimeError):
    pass


class DefaultConfig(Configuration):

    def __init__(self, timeout, newline, prompt, log_level):
        Configuration.__init__(self,
                timeout=TimeEntry(timeout or 3),
                newline=NewlineEntry(newline or 'LF'),
                prompt=StringEntry(prompt),
                log_level=LogLevelEntry(log_level or 'INFO'))


class ClientConfig(Configuration):

    def __init__(self, host, alias=None, port=22, timeout=3, newline='LF',
                 prompt=None, term_type='vt100', width=80, height=24):
        Configuration.__init__(self,
                host=StringEntry(host),
                alias=StringEntry(alias),
                port=IntegerEntry(port),
                timeout=TimeEntry(timeout),
                newline=NewlineEntry(newline),
                prompt=StringEntry(prompt),
                term_type=StringEntry(term_type),
                width=IntegerEntry(width),
                height=IntegerEntry(height))


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
