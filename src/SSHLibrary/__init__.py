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
import os
import glob
import re
import posixpath

from robot import utils

from connectioncache import ConnectionCache
from core import AuthenticationException, ClientConfig, SSHClientException
from config import (Configuration, StringEntry, NewlineEntry, TimeEntry,
        LogLevelEntry)
from deprecated import DeprecatedSSHLibraryKeywords
from version import VERSION
if utils.is_jython:
    from javaclient import JavaSSHClient as SSHClient
else:
    from pythonclient import PythonSSHClient as SSHClient

__version__ = VERSION


class SSHLibrary(DeprecatedSSHLibraryKeywords):
    """SSH Library is a test library for Robot Framework that enables
    executing commands and transferring files over an SSH connection.

    SSHLibrary works with both Python and Jython interpreters. To use
    SSHLibrary with Python, you must first install paramiko SSH
    implementation[1] and its dependencies.  To use SSHLibrary with Jython, you
    must have jar distribution of Trilead SSH implementation[2] in the
    CLASSPATH during test execution

    [1] http://www.lag.net/paramiko/
    [2] http://www.trilead.com/Products/Trilead_SSH_for_Java/

    Currently, there are two modes of operation:

    1. When keyword `Execute Command` or `Start Command` is used to execute
    something, a new channel is opened over the SSH connection. In practice it
    means that no session information is stored.

    2. Keywords `Write` and `Read XXX` operate in an interactive shell, which
    means that changes to state are visible to next keywords. Note that in
    interactive mode, a prompt must be set before using any of the
    Write-keywords. Prompt can be set either on `library importing` or
    when a new connection is opened using `Open Connection`, or using
    keywords `Set Prompt` or `Set Default Prompt`.

    Both modes require that a connection is opened with `Open Connection`.
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, timeout=3, newline='LF', prompt=None,
                 log_level='INFO'):
        """SSH Library allows some import time configuration.

        `timeout`, `newline` and `prompt` set default values for new
        connections opened with `Open Connection`. The default values may
        later be changed using `Set Default Configuration` and settings
        of a single connection with `Set Client Configuration`.

        `log_level` sets the default log level used to log return values of
        `Read Until` variants. It can also be later changed using `Set
        Default Configuration`.

        Examples:
        | Library | SSHLibrary | # use default values |
        | Library | SSHLibrary | timeout=10 | prompt=> |
        """
        self._cache = ConnectionCache()
        self._config = DefaultConfig(timeout, newline, prompt, log_level)

    @property
    def ssh_client(self):
        return self._cache.current

    def set_default_configuration(self, *entries):
        """Update the default configuration values.

        This keyword can only be used using named argument syntax. The names
        of accepted arguments are the same as can be given in the `library
        importing`.

        Example:
            | Set Default Configuration | newline=CRLF | prompt=$ |
        """
        self._config.update_with_strings(*entries)

    def set_client_configuration(self, *entries):
        """Update the client configuration values.

        Works on the currently selected connection. At least one connection
        must have been opened using `Open Connection`.

        This keyword can only be used using named argument syntax. The names
        of accepted arguments are the same as can be given to the `Open
        Connection` keyword.

        Example:
            | Set Client Configuration | term_type=ansi | timeout=2 hours |
        """
        self.ssh_client.config.update_with_strings(*entries)

    def open_connection(self, host, alias=None, port=22, timeout=None,
                        newline=None, prompt=None, term_type='vt100',
                        width=80, height=24):
        """Opens a new SSH connection to given `host` and `port`.

        Possible already opened connections are cached.

        Returns the index of this connection which can be used later to switch
        back to it. Indexing starts from 1 and is reset when `Close All`
        keyword is used.

        Optional `alias` is a name for the connection and it can be used for
        switching between connections similarly as the index. See `Switch
        Connection` for more details about that.

        If `timeout`, `newline` or `prompt` are not given, the default values
        set in `library importing` are used. See also `Set Default
        Configuration`.

        Starting from SSHLibrary 1.1, a shell session is also opened
        automatically by this keyword. `term_type` defines the terminal type
        for this shell, and `width` and `height` can be configured to control
        the virtual size of it.

        All of the client configuration options can be later updated using
        `Set Client Configuration`.

        Examples:
        | Open Connection | myhost.net |
        | Open Connection | yourhost.com | alias=2nd conn | port=23 |prompt=# |
        | Open Connection | myhost.net | term_type=ansi | width=40 |
        | ${id} =         | Open Connection | myhost.net |
        """
        config = ClientConfig(host, alias, port, timeout, newline, prompt,
                              term_type, width, height, self._config)
        return self._cache.register(SSHClient(config), config.alias)

    def switch_connection(self, index_or_alias):
        """Switches between active connections using index or alias.

        Index is got from `Open Connection` and alias can be given to it.

        Returns the index of previous connection, which can be used to restore
        the connection later.

        Example:

        | Open Connection       | myhost.net   |          |
        | Login                 | john         | secret   |
        | Execute Command       | some command |          |
        | Open Connection       | yourhost.com | 2nd conn |
        | Login                 | root         | password |
        | Start Command         | another cmd  |          |
        | Switch Connection     | 1            | # index  |
        | Execute Command       | something    |          |
        | Switch Connection     | 2nd conn     | # alias  |
        | Read Command Output   |              |          |
        | Close All Connections |              |          |

        Above example expects that there was no other open connections when
        opening the first one because it used index '1' when switching to it
        later. If you aren't sure about that you can store the index into
        a variable as below.

        | ${id} =            | Open Connection | myhost.net |
        | # Do something ... |
        | Switch Connection  | ${id}           |            |
        """
        old_index = self._cache.current_index
        self._cache.switch(index_or_alias)
        return old_index

    def close_all_connections(self):
        """Closes all open connections and empties the connection cache.

        After this keyword indices returned by `Open Connection` start from 1.

        This keyword ought to be used in test or suite teardown to make sure
        all connections are closed.
        """
        try:
            self._cache.close_all()
        except AttributeError:
            pass

    def enable_ssh_logging(self, logfile):
        """Enables logging of SSH protocol output to given `logfile`

        `logfile` can be relative or absolute path to a file that is writable
        by current user. In case that it already exists, it will be
        overwritten.

        Note that this keyword only works with Python, e.g. when executing the
        tests with `pybot`
        """
        if SSHClient.enable_logging(logfile):
            self._log('SSH log is written to <a href="%s">file</a>.' % logfile,
                      'HTML')

    def close_connection(self):
        """Closes the currently active connection.
        """
        self.ssh_client.close()

    def login(self, username, password):
        """Logs in to SSH server with given user information.

        Reads and returns available output. If prompt is set, everything until
        the prompt is returned.

        Example:
        | Login | john | secret |
        """
        self._log_login(username)
        self.ssh_client.login(username, password)
        self.ssh_client.open_shell()
        return self.read_until_prompt() if self.ssh_client.config.prompt else \
                    self.read()

    def login_with_public_key(self, username, keyfile, password):
        """Logs into SSH server with using key-based authentication.

        `username` is the username on the remote system.
        `keyfile` is a path to a valid OpenSSH *private* key file.
        `password` is used to unlock `keyfile` if unlocking is required.

        Reads and returns available output. If prompt is set, everything until
        the prompt is returned.

        """
        self._verify_key_file(keyfile)
        self._log_login(username)
        try:
            self.ssh_client.login_with_public_key(username, keyfile, password)
        except AuthenticationException:
            raise RuntimeError('Login with public key failed')
        return self.read_until_prompt() if self.ssh_client.config.prompt else \
                    self.read()

    def _log_login(self, username):
        self._info("Logging into '%s:%s' as '%s'."
                    % (self.ssh_client.host, self.ssh_client.port, username))

    def _verify_key_file(self, keyfile):
        if not os.path.exists(keyfile):
            raise RuntimeError("Given key file '%s' does not exist" % keyfile)
        try:
            open(keyfile).close()
        except IOError:
            raise RuntimeError("Could not read key file '%s'" % keyfile)

    def execute_command(self, command, return_stdout=True,
                        return_stderr=False, return_rc=False):
        """Executes command and returns combination of stdout, stderr and return code.

        `return_stdout`, `return_stderr` and `return_rc` are used to
        configure whether the return value includes the command's stdout,
        stderr or return code, respectively.  If only one of these evaluates
        to true, the corresponding value is returned.  Otherwise a tuple
        containing all requested values is returned.

        By default, only stdout is returned.

        This keyword waits until the command is completed. If non-blocking
        behavior is required, use `Start Command` instead.

        Multiple calls of `Execute Command` use separate SSH sessions. Thus,
        possible changes to the environment are not shared between these calls.
        `Write` and `Read XXX` keywords can be used for running multiple
        commands in the same session.

        Examples:
        | ${stdout}= | Execute Command | ${cmd} |
        | ${stdout} | ${stderr}= | Execute Command | ${cmd} | return_stderr=yes |
        | ${rc}= | Execute Command | ${cmd} | return_stdout=${EMPTY} | return_rc=true |

        In the first example, only stdout is returned, in the second, both
        stdout and stderr are returned and in the last only return code is
        returned.
        """
        self._info("Executing command '%s'" % command)
        opts = self._output_options(return_stdout, return_stderr, return_rc)
        return self.ssh_client.execute_command(command, *opts)

    def start_command(self, command):
        """Starts command execution on remote host.

        This keyword doesn't return anything. Use `Read Command Output` to read
        the output generated from command execution.

        Note that the `Read Command Output` keyword always reads the output of
        the most recently started command.

        Example:
        | Start Command | some command |
        """
        self._info("Starting command '%s'" % command)
        self._command = command
        self.ssh_client.start_command(command)

    def read_command_output(self, return_stdout=True, return_stderr=False,
                            return_rc=False):
        """Reads and returns/logs output (stdout and/or stderr) of a command.

        Command must have been started using `Start Command` before this
        keyword can be used.

        See `Execute Command` for examples about how the return value can
        be configured using `return_stdout`, `return_stderr` and `return_rc`.
        """
        self._info("Reading output of command '%s'" % self._command)
        opts = self._output_options(return_stdout, return_stderr, return_rc)
        return self.ssh_client.read_command_output(*opts)

    def _output_options(self, stdout, stderr, rc):
        # Handle legacy options for configuring returned outputs
        if not isinstance(stdout, basestring):
            return stdout, stderr, rc
        stdout = stdout.lower()
        if stdout == 'stderr':
            return False, True, rc
        if stdout == 'both':
            return True, True, rc
        return stdout, stderr, rc

    def write(self, text, loglevel=None):
        """Writes given text over the connection and appends newline.

        Consumes the written text (until the appended newline) from output
        and returns it. Given text must not contain newlines.

        Note: This keyword does not return the possible output of the executed
        command. To get the output, one of the `Read XXX` keywords must be
        used.
        """
        self._write(text, add_newline=True)
        return self.read_until(self._config.newline, loglevel)

    def write_bare(self, text):
        """Writes given text over the connection without appending newline.

        Unlike `Write` does not consume the written text from the output.
        """
        self._write(text)

    def _write(self, text, add_newline=False):
        self._info("Writing %s" % repr(text))
        try:
            self.ssh_client.write(text, add_newline)
        except SSHClientException, e:
            raise RuntimeError(e)

    def read(self, loglevel=None):
        """Reads and returns/logs everything currently available on the output.

        Read message is always returned and logged. Default log level is
        either 'INFO', or the level set with `Set Default Log Level`.
        `loglevel` can be used to override the default log level, and available
        levels are TRACE, DEBUG, INFO and WARN.

        This keyword is most useful for reading everything from the output
        buffer, thus clearing it.
        """
        ret = self.ssh_client.read()
        self._log(ret, loglevel)
        return ret

    def read_until(self, expected, loglevel=None):
        """Reads output until expected is encountered or timeout expires.

        Text up until and including the match will be returned, If no match is
        found, the keyword fails.

        The timeout is by default three seconds but can be changed either on
        `library importing` or by using `Set Timeout` keyword.

        See `Read` for more information on `loglevel`.
        """
        return self._read_until(expected, loglevel)

    def _read_until(self, expected, loglevel):
        ret = ''
        start_time = time.time()
        while time.time() < float(self._config.timeout) + start_time:
            ret += self.ssh_client.read_char()
            if (isinstance(expected, basestring) and expected in ret) or \
               (not isinstance(expected, basestring) and expected.search(ret)):
                self._log(ret, loglevel)
                return ret
        self._log(ret, loglevel)
        if not isinstance(expected, basestring):
            expected = expected.pattern
        raise AssertionError("No match found for '%s' in %s"
                % (expected, utils.secs_to_timestr(self._config.timeout)))

    def read_until_regexp(self, regexp, loglevel=None):
        """Reads output until a match to `regexp` is found or timeout expires.

        `regexp` can be a pattern or a compiled re-object.

        Returns text up until and including the regexp.

        The timeout is by default three seconds but can be changed either on
        `library importing` or by using `Set Timeout` keyword.

        See `Read` for more information on `loglevel`.
        Examples:
        | Read Until Regexp | (#|$) |
        | Read Until Regexp | some regexp  | DEBUG |
        """
        if isinstance(regexp, basestring):
            regexp = re.compile(regexp)
        return self._read_until(regexp, loglevel)

    def read_until_prompt(self, loglevel=None):
        """Reads and returns text from the output until prompt is found.

        Prompt must have been set, either in `library importing` or by using
        `Set Prompt` -keyword.

        See `Read` for more information on `loglevel`.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and the command does not
        produce prompt characters in its output.
        """
        return self.read_until(self.ssh_client.config.prompt, loglevel)

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes given text repeatedly until `expected` appears in output.

        `text` is written without appending newline. `retry_interval` defines
        the time that is waited before writing `text` again. `text` will be
        consumed from the output before `expected` is tried to be read.

        If `expected` does not appear on output within `timeout`, this keyword
        fails.

        See `Read` for more information on `loglevel`.

        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\n | myprocess |
        | ... | 5s | 0.5s |

        This will write the 'ps -ef | grep myprocess\\n' until 'myprocess'
        appears on the output. The command is written every 0.5 seconds and
        the keyword will fail if 'myprocess' does not appear on the output in
        5 seconds.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        old_timeout = self.set_timeout(retry_interval)
        starttime = time.time()
        while time.time() - starttime < timeout:
            self.write_bare(text)
            try:
                ret = self._read_until(expected, loglevel)
                self.set_timeout(old_timeout)
                return ret
            except AssertionError:
                pass
        self.set_timeout(old_timeout)
        raise AssertionError("No match found for '%s' in %s"
                             % (expected, utils.secs_to_timestr(timeout)))

    def put_file(self, source, destination='.', mode='0744', newlines='default'):
        """Copies file(s) from local host to remote host.

        1. If the destination is an existing file, the source file is copied
           over it.
        2. If the destination is an existing directory, the source file is
           copied into it. Possible file with same name is overwritten.
        3. If the destination does not exist and it ends with path separator
           ('/'), it is considered a directory. That directory is created and
           the source file copied into it. Possibly missing intermediate
           directories are also created.
        4. If the destination does not exist and it does not end with path
           separator, it is considered a file. If the path to the file does
           not exist it is created.
        5. If destination is not given, the user's home directory
           in the remote machine is used as destination.

        Using wild cards like '*' and '?' are allowed.
        When wild cards are used, destination MUST be a directory and only
        files are copied from the source, sub directories are ignored. If the
        contents of sub directories are also needed, use the keyword again.

        Default file permission is 0744 (-rwxr--r--) and can be changed by
        giving a value to the optional `mode` parameter.

        `newlines` can be used to force newline characters that are written to
        the remote file. Valid values are `CRLF` (for Windows) and `LF`.

        Examples:

        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt | # single file                    |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               | # multiple files with wild cards |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/  |  0777  | CRLF | # file permissions and forcing Windows newlines |

        """
        mode = int(mode, 8)
        self.ssh_client.create_sftp_client()
        localfiles = self._get_put_file_sources(source)
        remotefiles, remotepath = self._get_put_file_destinations(localfiles,
                                                                  destination)
        self.ssh_client.create_missing_remote_path(remotepath)
        for src, dst in zip(localfiles, remotefiles):
            self._info("Putting '%s' to '%s'" % (src, dst))
            newline = {'CRLF': '\r\n', 'LF': '\n'}.get(newlines, None)
            self.ssh_client.put_file(src, dst, mode, newline)
        self.ssh_client.close_sftp_client()

    def _get_put_file_sources(self, source):
        sources = [f for f in glob.glob(source.replace('/', os.sep))
                   if os.path.isfile(f)]
        if not sources:
            raise AssertionError("There were no source files matching '%s'" %
                                 source)
        self._debug('Source pattern matched local files: %s' %
                    utils.seq2str(sources))
        return sources

    def _get_put_file_destinations(self, sources, dest):
        dest = dest.split(':')[-1].replace('\\', '/')
        if dest == '.':
            dest = self.ssh_client.homedir + '/'
        if len(sources) > 1 and dest[-1] != '/':
            raise ValueError('It is not possible to copy multiple source '
                             'files to one destination file.')
        dirpath, filename = self._parse_path_elements(dest)
        if filename:
            files = [posixpath.join(dirpath, filename)]
        else:
            files = [posixpath.join(dirpath, os.path.split(path)[1])
                     for path in sources]
        return files, dirpath

    def _parse_path_elements(self, dest):
        if not posixpath.isabs(dest):
            dest = posixpath.join(self.ssh_client.homedir, dest)
        return posixpath.split(dest)

    def get_file(self, source, destination='.'):
        """Copies a file from remote host to local host.

        1. If the destination is an existing file, the source file is copied
           over it.
        2. If the destination is an existing directory, the source file is
           copied into it. Possible file with same name is overwritten.
        3. If the destination does not exist and it ends with path separator
           ('/' in unixes, '\\' in Windows), it is considered a directory.
           That directory is created and source file copied into it. Possible
           missing intermediate directories are also created.
        4. If the destination does not exist and it does not end with path
           separator, it is considered a file. If the path to the file does
           not exist it is created.
        5. If the destination is not given, the current working directory in
           the local machine is used as destination. This will most probably
           be the directory where test execution was started.

        Using wild cards like '*' and '?' are allowed.
        When wild cards are used, destination MUST be a directory, and files
        matching the pattern are copied, but sub directories are ignored. If
        the contents of sub directories are also needed, use the keyword again.

        Examples:

        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # single file                    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # multiple files with wild cards |

        """
        self.ssh_client.create_sftp_client()
        remotefiles = self._get_get_file_sources(source)
        self._debug('Source pattern matched remote files: %s' %
                    utils.seq2str(remotefiles))
        localfiles = self._get_get_file_destinations(remotefiles, destination)
        for src, dst in zip(remotefiles, localfiles):
            self._info('Getting %s to %s' % (src, dst))
            self.ssh_client.get_file(src, dst)
        self.ssh_client.close_sftp_client()

    def _get_get_file_sources(self, source):
        path, pattern = posixpath.split(source)
        if not path:
            path = '.'
        sourcefiles = []
        for filename in self.ssh_client.listfiles(path):
            if utils.matches(filename, pattern):
                if path:
                    filename = posixpath.join(path, filename)
                sourcefiles.append(filename)
        if not sourcefiles:
            raise AssertionError("There were no source files matching '%s'" %
                                 source)
        return sourcefiles

    def _get_get_file_destinations(self, sourcefiles, dest):
        if dest == '.':
            dest += os.sep
        is_dir = dest.endswith(os.sep)
        if not is_dir and len(sourcefiles) > 1:
            raise ValueError('It is not possible to copy multiple source '
                             'files to one destination file.')
        dest = os.path.abspath(dest.replace('/', os.sep))
        self._create_missing_local_dirs(dest, is_dir)
        if is_dir:
            return [os.path.join(dest, os.path.split(name)[1])
                    for name in sourcefiles]
        return [dest]

    def _create_missing_local_dirs(self, dest, is_dir):
        if not is_dir:
            dest = os.path.dirname(dest)
        if not os.path.exists(dest):
            self._info("Creating missing local directories for path '%s'" %
                        dest)
            os.makedirs(dest)

    def _info(self, msg):
        self._log(msg, 'INFO')

    def _debug(self, msg):
        self._log(msg, 'DEBUG')

    def _log(self, msg, level=None):
        self._is_valid_log_level(level, raise_if_invalid=True)
        msg = msg.strip()
        if level is None:
            level = self._config.log_level
        if msg != '':
            print '*%s* %s' % (level.upper(), msg)

    def _is_valid_log_level(self, level, raise_if_invalid=False):
        if level is None:
            return True
        if isinstance(level, basestring) and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN', 'HTML']:
            return True
        if not raise_if_invalid:
            return False
        raise AssertionError("Invalid log level '%s'" % level)


class DefaultConfig(Configuration):

    def __init__(self, timeout, newline, prompt, log_level):
        Configuration.__init__(self,
                timeout=TimeEntry(timeout or 3),
                newline=NewlineEntry(newline or 'LF'),
                prompt=StringEntry(prompt),
                log_level=LogLevelEntry(log_level or 'INFO'))
