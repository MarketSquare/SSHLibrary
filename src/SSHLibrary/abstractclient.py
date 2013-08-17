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

import os
import re
import stat
import time
import glob

from .config import (Configuration, StringEntry, TimeEntry, IntegerEntry,
        NewlineEntry)


class SSHClientException(RuntimeError):
    pass


class ClientConfig(Configuration):

    def __init__(self, host, alias=None, port=22, timeout=3, newline='LF',
                 prompt=None, term_type='vt100', width=80, height=24,
                 encoding='utf8'):
        Configuration.__init__(self,
                host=StringEntry(host),
                alias=StringEntry(alias),
                port=IntegerEntry(port),
                timeout=TimeEntry(timeout),
                newline=NewlineEntry(newline),
                prompt=StringEntry(prompt),
                term_type=StringEntry(term_type),
                width=IntegerEntry(width),
                height=IntegerEntry(height),
                encoding=StringEntry(encoding))


class AbstractSSHClient(object):
    """A base class for SSH client implementations, defines the public API

    Subclasses  provide the tool/language specific concrete implementations.
    """

    def __init__(self, host, alias=None, port=22, timeout=3, newline='LF',
                 prompt=None, term_type='vt100', width=80, height=24,
                 encoding='utf8'):
        """Create new SSHClient based on arguments."""
        self.config = ClientConfig(host, alias, port, timeout, newline,
                                   prompt, term_type, width, height, encoding)
        self.client = self._create_client()
        self._commands = []

    @property
    def host(self):
        return self.config.host

    @property
    def port(self):
        return self.config.port

    @staticmethod
    def enable_logging(path):
        """Log SSH events to file.

        :param path: A filename where the log events are written
        :returns: Whether logging was successfully enabled.
        """
        raise NotImplementedError

    def login(self, username, password):
        """Login using given credentials.

        :param str username: username to log in with
        :param str password: password for `username`
        :returns: If prompt is defined, read and return output until prompt.
            Otherwise all output is read and returned.
        """
        try:
            self._login(username, password)
        except SSHClientException:
            msg = 'Authentication failed for user: %s' % username
            raise SSHClientException(msg)
        return self._finalize_login()

    def login_with_public_key(self, username, keyfile, password):
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
            msg = 'Login with public key failed for user: %s' % username
            raise SSHClientException(msg)
        return self._finalize_login()

    def _finalize_login(self):
        self.open_shell()
        return self.read_until_prompt() if self.config.prompt else self.read()

    def _verify_key_file(self, keyfile):
        if not os.path.exists(keyfile):
            raise SSHClientException("Given key file '%s' does not exist" %
                                     keyfile)
        try:
            open(keyfile).close()
        except IOError:
            raise SSHClientException("Could not read key file '%s'" % keyfile)

    def execute_command(self, command):
        """Execute given command over existing connection.

        :returns: 3-tuple (stdout, stderr, return_code)
        """
        self.start_command(command)
        return self.read_command_output()

    def start_command(self, command):
        """Execute given command over existing connection."""
        command = command.encode(self.config.encoding)
        self._commands.append(self._start_command(command))

    def read_command_output(self):
        """Read output of a previously started command.

        :returns: 3-tuple (stdout, stderr, return_code)
        """
        return self._commands.pop().read_outputs()

    def write(self, text, add_newline=False):
        """Write `text` in shell session.

        :param str text: the text to be written
        :param bool add_newline: if True, a newline will be added to `text`.
        """
        text = text.encode(self.config.encoding)
        self._ensure_prompt_is_set()
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
        self._ensure_prompt_is_set()
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
        timeout = TimeEntry(timeout)
        interval = TimeEntry(interval)
        starttime = time.time()
        while time.time() - starttime < timeout.value:
            self.write(text)
            try:
                return self._read_until(lambda s: expected in s,
                                        expected, timeout=interval.value)
            except SSHClientException:
                pass
        raise SSHClientException("No match found for '%s' in %s."
                                 % (expected, timeout))

    def _read_until(self, matcher, expected, timeout=None):
        ret = ''
        timeout = TimeEntry(timeout) if timeout else self.config.get('timeout')
        start_time = time.time()
        while time.time() < float(timeout.value) + start_time:
            try:
                ret += self._read_char()
                decoded_string = ret.decode(self.config.encoding)
                if matcher(decoded_string):
                    return decoded_string
            except UnicodeDecodeError:
                pass
        raise SSHClientException("No match found for '%s' in %s\nOutput:\n%s"
                                 % (expected, timeout, ret))

    def _ensure_prompt_is_set(self):
        if not self.config.prompt:
            raise SSHClientException('Prompt is not set.')

    def put_file(self, source, destination='.', mode='0744',
                 newline='default', path_separator='/'):
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
        sftp_client = self._create_sftp_client()
        sources, destinations = sftp_client.put_file(source, destination, mode,
                                                     newline, path_separator)
        sftp_client.close()
        return sources, destinations

    def put_directory(self, source, destination='.', mode='0744',
                      newline='default', path_separator='/', recursive=False):
        sftp_client = self._create_sftp_client()
        sources, destinations = sftp_client.put_directory(source, destination,
                                                          mode, newline,
                                                          path_separator,
                                                          recursive)
        sftp_client.close()
        return sources, destinations

    def get_file(self, source, destination='.', path_separator='/'):
        """Get file(s) from the remote host to localhost.

        :param source: Remote file path. May be a simple pattern containing
            '*' and '?', in which case all matching files are tranferred
            :param destintation: Local path. If many files are transferred,
            must be a directory. Defaults to current working directory.
        :param path_separator: The path separator on the remote machine.
            Must be defined if the remote machine runs Windows.
        """
        sftp_client = self._create_sftp_client()
        sources, destinations = sftp_client.get_file(source, destination,
                                                     path_separator)
        sftp_client.close()
        return sources, destinations

    def get_directory(self, source, destination='.', path_separator='/',
                      recursive=False):
        sftp_client = self._create_sftp_client()
        sources, destinations = sftp_client.get_directory(source, destination,
                                                          path_separator,
                                                          recursive)
        sftp_client.close()
        return sources, destination

    def list_dir(self, path, pattern=None, absolute=False):
        sftp_client = self._create_sftp_client()
        items = sftp_client.list(sftp_client.listfiles, path, pattern, absolute)
        items += sftp_client.list(sftp_client.listdirs, path, pattern, absolute)
        sftp_client.close()
        items.sort()
        return items

    def list_files_in_dir(self, path, pattern=None, absolute=False):
        sftp_client = self._create_sftp_client()
        files = sftp_client.list(sftp_client.listfiles, path, pattern, absolute)
        sftp_client.close()
        files.sort()
        return files

    def list_dirs_in_dir(self, path, pattern=None, absolute=False):
        sftp_client = self._create_sftp_client()
        dirs = sftp_client.list(sftp_client.listdirs, path, pattern, absolute)
        sftp_client.close()
        dirs.sort()
        return dirs


class AbstractSFTPClient(object):

    def __init__(self, ssh_client):
        self._client = self._create_client(ssh_client)
        self._homedir = self._normalize_path('.')

    def close(self):
        self._client.close()

    def exists(self, path):
        try:
            self._client.stat(path)
        except IOError:
            return False
        return True

    def list(self, command, path, pattern=None, absolute=False):
        items = command(path)
        if pattern:
            items = self._filter_by_pattern(items, pattern)
        if absolute:
            items = self._include_absolute_path(items, path)
        return items

    def listfiles(self, path):
        return self._include_files_of_type(stat.S_ISREG, path)

    def listdirs(self, path):
        return self._include_files_of_type(stat.S_ISDIR, path)

    def _include_files_of_type(self, stat_type, path):
        return [fileinfo.filename for fileinfo in self._list(path)
                if stat_type(self._get_file_permissions(fileinfo)) and
                (fileinfo.filename not in ('.', '..'))]

    def _filter_by_pattern(self, items, pattern):
        return [name for name in items if fnmatchcase(name, pattern)]

    def _include_absolute_path(self, items, path):
        return [self._get_full_path(path) + name for name in items]

    def get_directory(self, source, destination, path_separator='/',
                      recursive=False):
        if source.endswith(path_separator):
            source = source[:-len(path_separator)]
        if not self.exists(source):
            msg = "There was no source path matching '%s'" % source
            raise SSHClientException(msg)
        remotefiles = []
        localfiles = []
        parent_dir = os.path.basename(source)
        subdirs = [parent_dir]
        local_target_exists = True if os.path.isdir(destination) else False
        for path in subdirs:
            if recursive:
                [subdirs.append(path_separator.join([path, subdir_name]))
                for subdir_name in self.listdirs(path)]
            remote_path = path + path_separator + "*"
            local_path = os.path.join(destination, path) + path_separator
            if not local_target_exists:
                local_path = local_path.replace(parent_dir + path_separator, '')
            r, l = self.get_file(remote_path, local_path, path_separator)
            remotefiles.extend(r)
            localfiles.extend(l)
        return remotefiles, localfiles

    def get_file(self, source, destination, path_separator='/'):
        remotefiles = self._get_get_file_sources(source, path_separator)
        localfiles = self._get_get_file_destinations(remotefiles, destination)
        for src, dst in zip(remotefiles, localfiles):
            self._get_file(src, dst)
        return remotefiles, localfiles

    def _get_get_file_sources(self, source, path_separator):
        if path_separator in source:
            path, pattern = source.rsplit(path_separator, 1)
        else:
            path, pattern = '', source
        if not path:
            path = '.'
        sourcefiles = []
        for filename in self.listfiles(path):
            if fnmatchcase(filename, pattern):
                if path:
                    filename = path_separator.join([path, filename])
                sourcefiles.append(filename)
        if not sourcefiles:
            msg = "There were no source files matching '%s'" % source
            raise SSHClientException(msg)
        return sourcefiles

    def _get_get_file_destinations(self, sourcefiles, dest):
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

    def put_directory(self, source, destination, mode, newline,
                      path_separator='/', recursive=False):
        if not os.path.isdir(source):
            msg = "There was no source path matching '%s'" % source
            raise SSHClientException(msg)
        localfiles = []
        remotefiles = []
        source = os.path.abspath(source)
        os.chdir(os.path.dirname(source))
        parent = os.path.basename(source)
        if destination.endswith(path_separator):
            destination = destination[:-len(path_separator)]
        remote_target_exists = True if self.exists(destination) else False
        for dirpath, _, filenames in os.walk(parent):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                if destination.endswith('.'):
                    remote_path = path_separator.join([dirpath, filename])
                else:
                    remote_path = path_separator.join([destination, dirpath, filename])
                    if not remote_target_exists:
                        remote_path = remote_path.replace(parent + path_separator, '')
                l, r = self.put_file(local_path, remote_path, mode, newline,
                                     path_separator)
                localfiles.extend(l)
                remotefiles.extend(r)
            if not recursive:
                break
        return localfiles, remotefiles

    def put_file(self, sources, destination, mode, newline,
                  path_separator='/'):
        mode = int(mode, 8)
        newline = {'CRLF': '\r\n', 'LF': '\n'}.get(newline.upper(), None)
        localfiles = self._get_put_file_sources(sources)
        remotefiles, remotedir = self._get_put_file_destinations(localfiles,
                                                                 destination,
                                                                 path_separator)
        self._create_missing_remote_path(remotedir)
        for src, dst in zip(localfiles, remotefiles):
            self._put_file(src, dst, mode, newline)
        return localfiles, remotefiles

    def _get_put_file_sources(self, source):
        sources = [f for f in glob.glob(source.replace('/', os.sep))
                   if os.path.isfile(f)]
        if not sources:
            msg = "There are no source files matching '%s'" % source
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

    def _get_full_path(self, path):
        full_path = self._normalize_path(path)
        if full_path[1:3] == ':\\':
            return full_path + '\\'
        else:
            return full_path + '/'

    def _normalize_path(self, path):
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

    def read_outputs(self):
        """Return outputs of this command.

        :return: a 3-tuple of stdout, stderr and return code.
        """
        raise NotImplementedError
