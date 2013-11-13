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

from __future__ import with_statement
from fnmatch import fnmatchcase
from robot.utils import unic
import os
import re
import stat
import time
import glob

from .config import (Configuration, IntegerEntry, NewlineEntry, StringEntry,
                     TimeEntry)


class SSHClientException(RuntimeError):
    pass


class _ClientConfiguration(Configuration):

    def __init__(self, host, alias, port, timeout, newline, prompt, term_type,
                 width, height, encoding):
        super(_ClientConfiguration, self).__init__(
            index=IntegerEntry(None),
            host=StringEntry(host),
            alias=StringEntry(alias),
            port=IntegerEntry(port),
            timeout=TimeEntry(timeout),
            newline=NewlineEntry(newline),
            prompt=StringEntry(prompt),
            term_type=StringEntry(term_type),
            width=IntegerEntry(width),
            height=IntegerEntry(height),
            encoding=StringEntry(encoding)
        )


class AbstractSSHClient(object):
    """A base class for SSH client implementations, defines the public API.

    Subclasses  provide the tool/language specific concrete implementations.
    """
    def __init__(self, host, alias=None, port=22, timeout=3, newline='LF',
                 prompt=None, term_type='vt100', width=80, height=24,
                 encoding='utf8'):
        self.config = _ClientConfiguration(host, alias, port, timeout, newline,
                                           prompt, term_type, width, height,
                                           encoding)
        self._sftp_client = None
        self._shell = None
        self._started_commands = []

    @staticmethod
    def enable_logging(path):
        """Log SSH events to file.

        :param path: A filename where the log events are written
        :returns: Whether logging was successfully enabled.
        """
        raise NotImplementedError

    @property
    def sftp_client(self):
        if not self._sftp_client:
            self._sftp_client = self._create_sftp_client()
        return self._sftp_client

    @property
    def shell(self):
        if not self._shell:
            self._shell = self._create_shell()
        return self._shell

    def _create_sftp_client(self):
        raise NotImplementedError

    def _create_shell(self):
        raise NotImplementedError

    def close(self):
        """Closes the connection.
        """
        self.client.close()

    def login(self, username, password, delay=None):
        """Login using given credentials.

        :param str username: username to log in with
        :param str password: password for `username`
        :returns: If prompt is defined, read and return output until prompt.
            Otherwise all output is read and returned.
        """
        try:
            self._login(username, password)
        except SSHClientException:
            msg = "Authentication failed for user '%s'." % username
            raise SSHClientException(msg)
        return self._read_login_output(delay)

    def _login(self, username, password):
        raise NotImplementedError

    def login_with_public_key(self, username, keyfile, password, delay=None):
        """Login using given credentials.

        :param str username: username to log in with
        :param str keyfile: path to a valid OpenSSH keyfile
        :param str password: password used in unlocking the keyfile
        :returns: If prompt is defined, read and return output until prompt.
            Otherwise all output is read and returned.
        """
        self._verify_key_file(keyfile)
        try:
            self._login_with_public_key(username, keyfile, password)
        except SSHClientException:
            msg = "Login with public key failed for user '%s'." % username
            raise SSHClientException(msg)
        return self._read_login_output(delay)

    def _login_with_public_key(self, username, keyfile, password):
        raise NotImplementedError

    def _read_login_output(self, delay):
        if self.config.prompt:
            return self.read_until_prompt()
        return self.read(delay)

    def _verify_key_file(self, keyfile):
        if not os.path.exists(keyfile):
            raise SSHClientException("Given key file '%s' does not exist." %
                                     keyfile)
        try:
            open(keyfile).close()
        except IOError:
            raise SSHClientException("Could not read key file '%s'." % keyfile)

    def execute_command(self, command):
        """Execute given command over existing connection.

        :returns: 3-tuple (stdout, stderr, return_code)
        """
        self.start_command(command)
        return self.read_command_output()

    def start_command(self, command):
        """Execute given command over existing connection."""
        command = self._encode(command)
        self._started_commands.append(self._start_command(command))

    def _encode(self, text):
        if isinstance(text, str):
            return text
        if not isinstance(text, basestring):
            text = unicode(text)
        return text.encode(self.config.encoding)

    def _start_command(self, command):
        raise NotImplementedError

    def read_command_output(self):
        """Read output of a previously started command.

        :returns: 3-tuple (stdout, stderr, return_code)
        """
        try:
            return self._started_commands.pop().read_outputs()
        except IndexError:
            raise SSHClientException('No started commands to read output from.')

    def write(self, text, add_newline=False):
        """Write `text` in shell session.

        :param str text: the text to be written
        :param bool add_newline: if True, a newline will be added to `text`.
        """
        text = self._encode(text)
        if add_newline:
            text += self.config.newline
        self.shell.write(text)

    def read(self, delay=None):
        """Read and return currently available output."""
        output = self.shell.read()
        if delay:
            output += self._delayed_read(delay)
        return self._decode(output)

    def _decode(self, output):
        return output.decode(self.config.encoding)

    def _delayed_read(self, delay):
        delay = TimeEntry(delay).value
        max_time = time.time() + self.config.get('timeout').value
        output = ''
        while time.time() < max_time:
            time.sleep(delay)
            read = self.shell.read()
            if not read:
                break
            output += read
        return output

    def read_char(self):
        """Read and return a single char from the current session."""
        server_output = ''
        while True:
            try:
                server_output += self.shell.read_byte()
                return self._decode(server_output)
            except UnicodeDecodeError:
                pass

    def read_until(self, expected):
        """Read and return from the output until expected.

        :param str expected: text to look for in the output
        :raises SSHClientException: if expected is not found in output when
            timeout expires.

        timeout is defined with :py:meth:`open_connection()`
        """
        return self._read_until(lambda s: expected in s, expected)

    def read_until_newline(self):
        """Read and return from the output up to the first newline character.

        :raises SSHClientException: if newline is not found in output when
            timeout expires.

        timeout is defined with :py:meth:`open_connection()`
        """
        return self.read_until(self.config.newline)

    def read_until_prompt(self):
        """Read and return from the output until prompt.

        :raises SSHClientException: if prompt is not set or it is not found
            in output when timeout expires.

        prompt and timeout are defined with :py:meth:`open_connection()`
        """
        if not self.config.prompt:
            raise SSHClientException('Prompt is not set.')
        return self.read_until(self.config.prompt)

    def read_until_regexp(self, regexp):
        """Read and return from the output until regexp matches.

        :param regexp: a pattern or a compiled regexp obect used for matching
        :raises SSHClientException: if match is not found in output when
            timeout expires.

        timeout is defined with :py:meth:`open_connection()`
        """
        if isinstance(regexp, basestring):
            regexp = re.compile(regexp)
        return self._read_until(lambda s: regexp.search(s), regexp.pattern)

    def write_until_expected(self, text, expected, timeout, interval):
        """Write text until expected output appears or timeout expires.

        :param str text: Text to be written using #write_bare().
        :param str expected: Text to look for in the output.
        :param int timeout: The timeout during which `expected` must appear
            in the output. Can be defined either as seconds or as a Robot
            Framework time string, e.g. 1 minute 20 seconds.
        :param int interval: Time to wait between repeated writings. Can be
            defined similarly as `timeout`.
        """
        interval = TimeEntry(interval)
        timeout = TimeEntry(timeout)
        max_time = time.time() + timeout.value
        while time.time() < max_time:
            self.write(text)
            try:
                return self._read_until(lambda s: expected in s, expected,
                                        timeout=interval.value)
            except SSHClientException:
                pass
        raise SSHClientException("No match found for '%s' in %s."
                                 % (expected, timeout))

    def _read_until(self, matcher, expected, timeout=None):
        server_output = ''
        timeout = TimeEntry(timeout) if timeout else self.config.get('timeout')
        max_time = time.time() + timeout.value
        while time.time() < max_time:
            try:
                server_output += self.shell.read_byte()
                decoded_output = self._decode(server_output)
                if matcher(decoded_output):
                    return decoded_output
            except UnicodeDecodeError:
                pass
        raise SSHClientException("No match found for '%s' in %s\nOutput:\n%s."
                                 % (expected, timeout, decoded_output))

    def put_file(self, source, destination='.', mode='0744', newline='',
                 path_separator='/'):
        """Put file(s) from localhost to remote host.

        :param source: Local file path. May be a simple pattern containing
            '*' and '?', in which case all matching files are tranferred
        :param destintation: Remote path. If many files are transferred,
            must be a directory. Defaults to users home directory.
        :param mode: File permissions for the remote file. Defined as a
            Unix file format string, e.g. '0600'
        :param newline: Newline character to be used in the remote file.
            Default is 'LF', i.e. the line feed character.
        :param path_separator: The path separator on the remote machine.
            Must be defined if the remote machine runs Windows.
        """
        return self.sftp_client.put_file(source, destination,
                                         mode, newline,
                                         path_separator)

    def put_directory(self, source, destination='.', mode='0744', newline='',
                      path_separator='/', recursive=False):
        return self.sftp_client.put_directory(source,
                                              destination,
                                              mode,
                                              newline,
                                              path_separator,
                                              recursive)

    def get_file(self, source, destination='.', path_separator='/'):
        """Get file(s) from the remote host to localhost.

        :param source: Remote file path. May be a simple pattern containing
            '*' and '?', in which case all matching files are tranferred
            :param destintation: Local path. If many files are transferred,
            must be a directory. Defaults to current working directory.
        :param path_separator: The path separator on the remote machine.
            Must be defined if the remote machine runs Windows.
        """
        return self.sftp_client.get_file(source, destination, path_separator)

    def get_directory(self, source, destination='.', path_separator='/',
                      recursive=False):
        return self.sftp_client.get_directory(source,
                                              destination,
                                              path_separator,
                                              recursive)

    def list_dir(self, path, pattern=None, absolute=False):
        items = self.sftp_client.list(path, pattern, absolute)
        return sorted(items)

    def list_files_in_dir(self, path, pattern=None, absolute=False):
        files = self.sftp_client.list_files(path, pattern, absolute)
        return sorted(files)

    def list_dirs_in_dir(self, path, pattern=None, absolute=False):
        dirs = self.sftp_client.list_dirs(path, pattern, absolute)
        return sorted(dirs)

    def dir_exists(self, path):
        return self.sftp_client.is_dir(path)

    def file_exists(self, path):
        return self.sftp_client.is_file(path)


class AbstractShell(object):

    def read(self):
        raise NotImplementedError

    def read_byte(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError


class SFTPFileInfo(object):

    def __init__(self, name, mode):
        self.name = unic(name)
        self.mode = mode

    def is_regular(self):
        return stat.S_ISREG(self.mode)

    def is_directory(self):
        return stat.S_ISDIR(self.mode)


class AbstractSFTPClient(object):

    def __init__(self):
        self._homedir = self._absolute_path('.')

    def _absolute_path(self, path):
        raise NotImplementedError

    def is_file(self, path):
        try:
            item = self._stat(path)
        except IOError:
            return False
        return item.is_regular()

    def _stat(self):
        raise NotImplementedError

    def is_dir(self, path):
        try:
            item = self._stat(path)
        except IOError:
            return False
        return item.is_directory()

    def list(self, path, pattern=None, absolute=False):
        return self._list_filtered(path, self._get_item_names, pattern,
                                   absolute)

    def _list_filtered(self, path, filter_method, pattern=None, absolute=False):
        self._verify_dir_exists(path)
        items = filter_method(path)
        if pattern:
            items = self._filter_by_pattern(items, pattern)
        if absolute:
            items = self._include_absolute_path(items, path)
        return items

    def _verify_dir_exists(self, path):
        if not self.is_dir(path):
            raise SSHClientException("There was no directory matching '%s'." % path)

    def _get_item_names(self, path):
        return [item.name for item in self._list(path)]

    def _list(self, path):
        raise NotImplementedError

    def _filter_by_pattern(self, items, pattern):
        return [name for name in items if fnmatchcase(name, pattern)]

    def _include_absolute_path(self, items, path):
        absolute_path = self._absolute_path(path)
        if absolute_path[1:3] == ':\\':
            absolute_path += '\\'
        else:
            absolute_path += '/'
        return [absolute_path + name for name in items]

    def list_files(self, path, pattern=None, absolute=False):
        return self._list_filtered(path, self._get_file_names, pattern,
                                   absolute)

    def _get_file_names(self, path):
        return [item.name for item in self._list(path) if item.is_regular()]

    def list_dirs(self, path, pattern=None, absolute=False):
        return self._list_filtered(path, self._get_directory_names, pattern,
                                   absolute)

    def _get_directory_names(self, path):
        return [item.name for item in self._list(path) if item.is_directory()]

    def get_directory(self, source, destination, path_separator='/',
                      recursive=False):
        source = self._remove_ending_path_separator(path_separator, source)
        self._verify_dir_exists(source)
        files = []
        for child in self.list(source):
            remote = source + path_separator + child
            local = os.path.join(destination, child)
            if self.is_file(remote):
                files += self.get_file(remote, local)
            elif recursive:
                files += self.get_directory(remote, local, path_separator, recursive)
        return files

    def _remove_ending_path_separator(self, path_separator, source):
        if source.endswith(path_separator):
            source = source[:-len(path_separator)]
        return source

    def get_file(self, source, destination, path_separator='/'):
        remote_files = self._get_remote_file_paths(source, path_separator)
        if not remote_files:
            msg = "There were no source files matching '%s'." % source
            raise SSHClientException(msg)
        local_files = self._get_local_file_paths(remote_files, destination)
        files = zip(remote_files, local_files)
        for src, dst in files:
            self._get_file(src, dst)
        return files

    def _get_remote_file_paths(self, source, path_separator):
        if path_separator in source:
            path, pattern = source.rsplit(path_separator, 1)
        else:
            path, pattern = '', source
        if not path:
            path = '.'
        return [filename for filename in
                self.list_files(path, pattern, absolute=True)]

    def _get_local_file_paths(self, sourcefiles, dest):
        if dest == '.':
            dest += os.sep
        is_dir = dest.endswith(os.sep)
        if not is_dir and len(sourcefiles) > 1:
            msg = 'Cannot copy multiple source files to one destination file.'
            raise SSHClientException(msg)
        dest = os.path.abspath(dest.replace('/', os.sep))
        self._create_missing_local_dirs(dest, is_dir)
        if is_dir:
            return [os.path.join(dest, os.path.basename(name))
                    for name in sourcefiles]
        return [dest]

    def _create_missing_local_dirs(self, dest, is_dir):
        if not is_dir:
            dest = os.path.dirname(dest)
        if not os.path.exists(dest):
            os.makedirs(dest)

    def _get_file(self, src, dst):
        raise NotImplementedError

    def put_directory(self, source, destination, mode, newline,
                      path_separator='/', recursive=False):
        if not os.path.isdir(source):
            msg = "There was no source path matching '%s'." % source
            raise SSHClientException(msg)
        files = []
        source = os.path.abspath(source)
        os.chdir(os.path.dirname(source))
        parent = os.path.basename(source)
        if destination.endswith(path_separator):
            destination = destination[:-len(path_separator)]
        remote_target_exists = True if self.is_dir(destination) else False
        for dirpath, _, filenames in os.walk(parent):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                if destination.endswith('.'):
                    remote_path = path_separator.join([dirpath, filename])
                else:
                    remote_path = path_separator.join([destination, dirpath,
                                                       filename])
                    if not remote_target_exists:
                        remote_path = remote_path.replace(parent +
                                                          path_separator, '')
                files += self.put_file(local_path, remote_path, mode, newline,
                                     path_separator)
            if not recursive:
                break
        return files

    def put_file(self, sources, destination, mode, newline, path_separator='/'):
        mode = int(mode, 8)
        newline = {'CRLF': '\r\n', 'LF': '\n'}.get(newline.upper(), None)
        localfiles = self._get_put_file_sources(sources)
        remotefiles, remotedir = self._get_put_file_destinations(localfiles,
                                                                 destination,
                                                                 path_separator)
        self._create_missing_remote_path(remotedir)
        files = zip(localfiles, remotefiles)
        for src, dst in files:
            self._put_file(src, dst, mode, newline)
        return files

    def _get_put_file_sources(self, source):
        sources = [f for f in glob.glob(source.replace('/', os.sep))
                   if os.path.isfile(f)]
        if not sources:
            msg = "There are no source files matching '%s'." % source
            raise SSHClientException(msg)
        return sources

    def _get_put_file_destinations(self, sources, dest, path_separator):
        dest = dest.split(':')[-1].replace('\\', '/')
        if dest == '.':
            dest = self._homedir + '/'
        if len(sources) > 1 and dest[-1] != '/':
            raise ValueError('It is not possible to copy multiple source '
                             'files to one destination file.')
        dirpath, filename = self._parse_path_elements(dest, path_separator)
        if filename:
            files = [path_separator.join([dirpath, filename])]
        else:
            files = [path_separator.join([dirpath, os.path.basename(path)])
                     for path in sources]
        return files, dirpath

    def _parse_path_elements(self, dest, path_separator):
        def _isabs(path):
            if dest.startswith(path_separator):
                return True
            if path_separator == '\\' and path[1:3] == ':\\':
                return True
            return False
        if not _isabs(dest):
            dest = path_separator.join([self._homedir, dest])
        return dest.rsplit(path_separator, 1)

    def _create_missing_remote_path(self, path):
        if path.startswith('/'):
            curdir = '/'
        else:
            curdir = self._client._absolute_path('.')
        for dirname in path.split('/'):
            if dirname:
                curdir = '%s/%s' % (curdir, dirname)
            try:
                self._client.stat(curdir)
            except:
                self._client.mkdir(curdir, 0744)

    def _put_file(self, source, destination, mode, newline):
        remotefile = self._create_remote_file(destination, mode)
        with open(source, 'rb') as localfile:
            position = 0
            while True:
                data = localfile.read(4096)
                if not data:
                    break
                if newline and '\n' in data:
                    data = data.replace('\n', newline)
                self._write_to_remote_file(remotefile, data, position)
                position += len(data)
            self._close_remote_file(remotefile)

    def _create_remote_file(self, destination, mode):
        raise NotImplementedError

    def _write_to_remote_file(self, remotefile, data, position):
        raise NotImplementedError

    def _close_remote_file(self, remotefile):
        raise NotImplementedError


class AbstractCommand(object):
    """Base class for remote commands."""

    def __init__(self, command, encoding):
        self._command = command
        self._encoding = encoding
        self._session = None

    def run_in(self, session):
        """Run this command in given SSH session.

        :param session: a session in an already open SSH connection
        """
        self._session = session
        self._execute()

    def _execute(self):
        raise NotImplementedError

    def read_outputs(self):
        """Return outputs of this command.

        :return: a 3-tuple of stdout, stderr and return code.
        """
        raise NotImplementedError
