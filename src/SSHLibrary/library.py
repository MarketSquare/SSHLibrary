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

from robot.utils import ConnectionCache

from .abstractclient import SSHClientException
from .client import SSHClient
from config import (Configuration, StringEntry, TimeEntry, LogLevelEntry,
        NewlineEntry)
from .deprecated import DeprecatedSSHLibraryKeywords
from .version import VERSION

__version__ = VERSION


class SSHLibrary(DeprecatedSSHLibraryKeywords):
    """Robot Framework test library for SSH and SFTP.

    SSHLibrary works with both Python and Jython interpreters.

    To use SSHLibrary with Python, you must first install Paramiko SSH
    implementation[1]. For Jython, you must have the JAR distribution of
    Trilead SSH implementation[2] in the CLASSPATH during the test execution.

    | [1] https://github.com/paramiko/paramiko
    | [2] http://robotframework-sshlibrary.googlecode.com/files/trilead-ssh2-build213.jar

    The library supports multiple connections to different hosts.
    New connections are opened with `Open Connection` keyword.

    Only one connection is active at a time. This means that keywords
    executed only affect the active connection. Active connection can be
    switched using `Switch Connection` keyword.

    For executing commands on the remote host, there are two possibilities:

    1. `Execute Command` or `Start Command`. These keywords open a new session
    using the connection. Possible state changes are not preserved.

    2. Keywords `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
    `Read Command Output`, `Read Until`, `Read Until Prompt` and
    `Read Until Regexp` operate in an interactive shell, which
    means that changes to state are visible to next keywords. Note that in
    interactive mode, prompt must be set before using any of the
    Write-keywords.

    Prompt, as well as the other settings, can be configured as defaults for
    all the upcoming connections on `library importing` or later by using
    `Set Default Configuration`. Settings overriding these defaults can be
    given as arguments to `Open Connection`. Currently active, already open
    connection can be configured with `Set Client Configuration`.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, timeout=3, newline='LF', prompt=None, loglevel='INFO',
                 encoding='UTF-8'):
        """SSH Library allows some import time configuration.

        `timeout`, `newline`, `prompt` and `encoding` all set default values for
        new connections opened with `Open Connection`.

        Starting from SSHLibrary 1.2, `encoding` is assumed as UTF-8 by
        default.

        The default values may later be changed with `Set Default Configuration`
        and settings of the active, already open connection with
        `Set Client Configuration`.

        `loglevel` sets the default log level used to log the return values of
        `Read Until` variants. It can also be later changed with `Set
        Default Configuration`.

        Examples:
        | Library | SSHLibrary | # use default values |
        | Library | SSHLibrary | timeout=10 | prompt=> |
        """
        self._cache = ConnectionCache()
        self._config = DefaultConfig(timeout, newline, prompt, loglevel,
                                     encoding)

    @property
    def ssh_client(self):
        return self._cache.current

    def set_default_configuration(self, timeout=None, newline=None,
                                  prompt=None, loglevel=None, encoding=None):
        """Update the default configuration values.

        Only parameters whose value is other than `None` are updated.

        Example:
        | Set Default Configuration | newline=CRLF | prompt=$ |
        """
        self._config.update(timeout=timeout, newline=newline, prompt=prompt,
                            loglevel=loglevel, encoding=encoding)

    def set_client_configuration(self, timeout=None, newline=None, prompt=None,
                                 term_type='vt100', width=80, height=24,
                                 encoding=None):
        """Update the client configuration values.

        Works on the currently active connection. At least one connection
        must have been opened using `Open Connection`.

        Only parameters whose value is other than `None` are updated.

        Example:
        | Set Client Configuration | term_type=ansi | timeout=2 hours |
        """
        self.ssh_client.config.update(timeout=timeout, newline=newline,
                                      prompt=prompt, term_type=term_type,
                                      width=width, height=height,
                                      encoding=encoding)

    def open_connection(self, host, alias=None, port=22, timeout=None,
                        newline=None, prompt=None, term_type='vt100', width=80,
                        height=24, encoding=None):
        """Opens a new SSH connection to given `host` and `port`.

        Possible already opened connections are cached.

        Returns the index of this connection which can be used later to switch
        back to it. Indices start from '1' and are reset when `Close All
        Connections` keyword is used.

        Optional `alias` can be given as a name for the connection and can be
        used for switching between connections similarly as the index.
        See `Switch Connection` for more details.

        If `timeout`, `newline`, `prompt` or `encoding` are not given,
        the default values set on `library importing` or set with
        `Set Default Configuration` are used.

        Starting from SSHLibrary 1.1, a shell session is also opened
        automatically by this keyword. `term_type` defines the terminal type
        for this shell, and `width` and `height` can be configured to control
        the virtual size of it.

        Client configuration options other than `host`, `port` and `alias`
        can be later updated with `Set Client Configuration`.

        Examples:
        | Open Connection | myhost.net |
        | Open Connection | yourhost.com | alias=2nd conn | port=23 |prompt=# |
        | Open Connection | myhost.net | term_type=ansi | width=40 |
        | ${index} =      | Open Connection | myhost.net |
        """
        timeout = timeout or self._config.timeout
        newline = newline or self._config.newline
        prompt = prompt or self._config.prompt
        encoding = encoding or self._config.encoding
        client = SSHClient(host, alias, port, timeout, newline, prompt,
                           term_type, width, height, encoding)
        return self._cache.register(client, alias)

    def get_connection_id(self):
        """Returns the index of the currently active connection.

        If no connection is currently active, `None` is returned.

        Example:
        | ${old_connection} = | Get Connection Id |
        | Open Connection     | yourhost.com |
        | # Do something with yourhost.com | |
        | Close Connection    | |
        | Switch Connection   | ${old_connection} |
        """
        return self._cache.current_index

    def switch_connection(self, index_or_alias):
        """Switches the active connection by index or alias.

        Index is got from `Open Connection` or from `Get Connection Id`.
        If `None` is given as argument `index_or_alias`, the currently active
        connection is is closed.

        The keyword always returns the index of the previous active connection,
        which can be used to reuse that connection later.

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
        opening the first one. Thus index '1' can be used to switch to it
        later. If you aren't sure about connection index you can store it
        into a variable as below:

        | ${index} =            | Open Connection | myhost.net |
        | # Do something ... |
        | Switch Connection  | ${index}           |            |
        """
        old_index = self.get_connection_id()
        if index_or_alias is None:
            self.close_connection()
        else:
            self._cache.switch(index_or_alias)
        return old_index

    def close_all_connections(self):
        """Closes all the open connections and empties the connection cache.

        After this, the connection indices returned by `Open Connection` start
        from 1.

        This keyword is ought to be used either in test or suite teardown to
        make sure all the connections are closed before the test execution
        finishes.
        """
        self._cache.close_all()

    def get_connections(self):
        """Return information about all the open connections.

        The return value is a list of objects that describe the connection.
        These objects have attributes that correspond to the argument names
        of `Open Connection`.

        Connection information is also logged.

        Example:
        | Open Connection | somehost  | prompt=>> |
        | Open Connection | otherhost | timeout=5 minutes |
        | ${conn1} | ${conn2}= | Get Connections |
        | Should Be Equal | ${conn1.host} | somehost |
        | Should Be Equal | ${conn2.timeout} | 5 minutes |
        """
        # TODO: could the ConnectionCache be enhanced to be iterable?
        configs = [c.config for c in self._cache._connections]
        for c in configs:
            self._log(str(c))
        return configs

    def enable_ssh_logging(self, logfile):
        """Enables logging of SSH protocol output to given `logfile`

        `logfile` can be relative or absolute path to a file that is writable
        by the current user. If the `logfile` already exists, it will be
        overwritten.

        Note that this keyword only works with Python, i.e. when executing
        tests with `pybot`.
        """
        if SSHClient.enable_logging(logfile):
            self._log('SSH log is written to <a href="%s">file</a>.' % logfile,
                      'HTML')

    def close_connection(self):
        """Closes the currently active connection."""
        self.ssh_client.close()
        self._cache.current = self._cache._no_current

    def login(self, username, password):
        """Logs into the SSH server using the given `username` and `password`.

        Reads and returns the output from the server. If prompt is set,
        everything until the prompt is returned.

        Example:
        | Login | john | secret |
        """
        return self._login(self.ssh_client.login, username, password)

    def login_with_public_key(self, username, keyfile, password):
        """Logs into the SSH server using key-based authentication.

        `username` is the username on the remote system.
        `keyfile` is a path to a valid OpenSSH private key file on the local
        filesystem.
        `password` is used to unlock the `keyfile` if unlocking is required.

        Reads and returns the output from the server. If prompt is set,
        everything until the prompt is returned.
        """
        return self._login(self.ssh_client.login_with_public_key, username,
                           keyfile, password)

    def _login(self, login_method, username, *args):
        self._info("Logging into '%s:%s' as '%s'."
                   % (self.ssh_client.host, self.ssh_client.port, username))
        try:
            return login_method(username, *args)
        except SSHClientException, e:
            raise RuntimeError(e)

    def execute_command(self, command, return_stdout=True,
                        return_stderr=False, return_rc=False):
        """Executes the command and returns a combination of stdout, stderr
        and return code.

        If several arguments evaluate true, a tuple containing the values
        is returned. `return_stdout`, `return_stderr` and `return_rc`
        can be used to configure whether the tuple contains all these values.
        If only one of the arguments evaluates true, the corresponding value is
        returned instead of a tuple.

        By default, only the command stdout is returned as a value:
        | ${stdout}= | Execute Command | ${cmd} |

        Example that returns both stdout and stderr as a tuple:
        | ${stdout} | ${stderr}= | Execute Command | ${cmd} | return_stderr=yes |

        Example that returns only the return code as a value:
        | ${rc}= | Execute Command | ${cmd} | return_stdout=${EMPTY} | return_rc=true |

        This keyword waits until the command is completed. If non-blocking
        behavior is required, use `Start Command` instead.

        Multiple calls of `Execute Command` use separate SSH sessions. Thus,
        possible changes to the environment are not shared between these calls.
        `Write` and `Read XXX` keywords can be used for running multiple
        commands in the same session.
        """
        self._info("Executing command '%s'" % command)
        opts = self._output_options(return_stdout, return_stderr, return_rc)
        stdout, stderr, rc = self.ssh_client.execute_command(command)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def start_command(self, command):
        """Starts command execution on the remote host and returns immediately.

        This keyword doesn't return anything. Use `Read Command Output` to read
        the output generated by the command execution.

        Note that the `Read Command Output` keyword always reads the output of
        the most recently started command.

        Example:
        | Start Command | ./myjobscript.sh |
        """
        self._info("Starting command '%s'" % command)
        self._last_command = command
        self.ssh_client.start_command(command)

    def read_command_output(self, return_stdout=True, return_stderr=False,
                            return_rc=False):
        """Reads output of the most recent started command and returns stdout,
        stderr and/or return value of the command.

        Command must have been started using `Start Command` before this
        keyword can be used.

        See `Execute Command` for examples about how the return value can
        be configured using `return_stdout`, `return_stderr` and `return_rc`.
        """
        self._info("Reading output of command '%s'" % self._last_command)
        opts = self._output_options(return_stdout, return_stderr, return_rc)
        stdout, stderr, rc = self.ssh_client.read_command_output()
        return self._return_command_output(stdout, stderr, rc, *opts)

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

    def _return_command_output(self, stdout, stderr, rc, return_stdout,
                               return_stderr, return_rc):
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

    def write(self, text, loglevel=None):
        """Writes the given `text` over the connection and appends a newline.

        Consumes the written `text` (until the appended newline) from output
        and returns it. Given `text` must not contain newlines.

        Note: This keyword does not return the possible output of the executed
        command. To get the output, one of the `Read XXX` keywords must be
        used.
        """
        self._write(text, add_newline=True)
        return self._read_and_log(loglevel, self.ssh_client.read_until_newline)

    def write_bare(self, text):
        """Writes the given `text` over the connection without appending
        a newline.

        Unlike `Write`, this keyword does not consume the written text from
        the output.
        """
        self._write(text)

    def _write(self, text, add_newline=False):
        self._info("Writing %s" % text)
        try:
            self.ssh_client.write(text, add_newline)
        except SSHClientException, e:
            raise RuntimeError(e)

    def read(self, loglevel=None):
        """Reads and returns everything currently available on the output.

        This keyword is most useful for reading everything from the output.
        After being read, the output buffer is cleared.

        This keyword also logs the read output. Default log level is set
        either on `library importing` or with `Set Default Configuration`.

        `loglevel` can be used to override the default log level.
        Possible levels are TRACE, DEBUG, INFO and WARN.
        """
        return self._read_and_log(loglevel, self.ssh_client.read)

    def read_until(self, expected, loglevel=None):
        """Reads output until the `expected` is encountered or timeout expires.

        Text up until and including the `expected` will be returned.
        If no match is found, the keyword fails.

        The timeout is three seconds by default. Timeout can be changed
        either on `library importing`, by using keywords
        `Set Default Configuration` or `Set Client Configuration`,
        or when opening a new connection with `Open Connection`.

        This keyword also logs the read output.
        See `Read` for more information on `loglevel`.
        """
        return self._read_and_log(loglevel, self.ssh_client.read_until,
                                  expected)

    def read_until_regexp(self, regexp, loglevel=None):
        """Reads output until a match to `regexp` is found or timeout expires.

        `regexp` can be a pattern or a compiled regexp-object.

        Returns text up until and including the `regexp.

        The timeout is three seconds by default. Timeout can be changed
        either on `library importing`, by using keywords
        `Set Default Configuration` or `Set Client Configuration`,
        or when opening a new connection with `Open Connection`.

        This keyword also logs the read output.
        See `Read` for more information on `loglevel`.

        Example:
        | Read Until Regexp | (#|$) |

        Example that logs the read output with level DEBUG:
        | Read Until Regexp | some regexp  | DEBUG |
        """
        return self._read_and_log(loglevel, self.ssh_client.read_until_regexp,
                                  regexp)

    def read_until_prompt(self, loglevel=None):
        """Reads and returns text from the output until the prompt is found.

        Prompt must have been set, either on `library importing` or when
        the connection was opened using `Open Connection`.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and the command does not
        produce prompt characters in its output.

        This keyword also logs the read output.
        See `Read` for more information on `loglevel`.
        """
        return self._read_and_log(loglevel, self.ssh_client.read_until_prompt)

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes given `text` repeatedly until `expected` appears in
        the output.

        `text` is written without appending a newline. `retry_interval` defines
        the time before writing `text` again. `text` will be consumed from
        the output before `expected` is read.

        If `expected` does not appear in output within `timeout`, this keyword
        fails.

        This keyword also logs the read output.
        See `Read` for more information on `loglevel`.

        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\n | myprocess |
        | ... | 5s | 0.5s |

        This will write the  'ps -ef | grep myprocess\\n' until 'myprocess'
        appears on the output. The command is written every 0.5 seconds and
        the keyword will fail if 'myprocess' does not appear in the output in
        5 seconds.
        """
        self._read_and_log(loglevel, self.ssh_client.write_until_expected,
                           text, expected, timeout, retry_interval)

    def _read_and_log(self, loglevel, reader, *args):
        try:
            output = reader(*args)
        except SSHClientException, e:
            raise RuntimeError(e)
        self._log(output, loglevel)
        return output

    def get_file(self, source, destination='.', path_separator='/'):
        """Copies file(s) from the remote host (`source`) to the local host
        (`destination`).

        1. If the `destination` is an existing file, the `source` file is copied
           over it.
        2. If the `destination` is an existing directory, the `source` file is
           copied into it. Possible file with the same name is overwritten.
        3. If the `destination` does not exist and it ends with the path
           separator ('/' in POSIXes, '\\' in Windows), it is considered a
           directory. The directory is then created and `source` file copied
           into it. Possible missing intermediate directories are also created.
        4. If the `destination` does not exist and it does not end with the path
           separator, it is considered a file. If the path to the file does
           not exist, it is created.
        5. If `destination` is not given, the current working directory in
           the local machine is used as the destination. This will most probably
           be the directory where the test execution was started.

        Using wildcards like '*' and '?' is possible in the `source`.
        When wildcards are used, `destination` MUST be a directory, and files
        matching the pattern are copied, but subdirectories are ignored. If
        the contents of subdirectories are also needed, use the keyword again.

        `path_separator` is the path separator character used in the remote
        machine. With Windows machines, this must be defined as '\\'.
        This option was added in SSHLibrary 1.1.

        Examples:
        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # single file                    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # multiple files with wild cards |

        """
        return self._run_sftp_command(self.ssh_client.get_file, source,
                                      destination, path_separator)

    def put_file(self, source, destination='.', mode='0744',
                 newline='default', path_separator='/'):
        """Copies file(s) from the local host (`source`) to the remote host
        (`destination`).

        1. If the `destination` is an existing file, the `source` file is copied
           over it.
        2. If the `destination` is an existing directory, the `source` file is
           copied into it. Possible file with same name is overwritten.
        3. If the `destination` does not exist and it ends with the path
           separator ('/' in POSIXes, '\\' in Windows), it is considered a
           directory. The directory is then created and the `source` file copied
           into it. Possibly missing intermediate directories are also created.
        4. If the `destination` does not exist and it does not end with the path
           separator, it is considered a file. If the path to the file does
           not exist it is created.
        5. If `destination` is not given, the user's home directory
           in the remote machine is used as the destination.

        Using wildcards like '*' and '?' is possible in the `source`.
        When wildcards are used, `destination` MUST be a directory and only
        files are copied from the `source`, subdirectories being ignored. If the
        contents of subdirectories are also needed, use the keyword again.

        Default file permission is 0744 (-rwxr--r--) and can be changed by
        giving a value to the optional `mode` parameter.

        `newline` can be used to force newline characters that are written to
        the remote file. Valid values are `CRLF` (for Windows) and `LF`.

        `path_separator` is the path separator character used in the remote
        machine. With Windows machines, this must be defined as '\\'.
        This option was added in SSHLibrary 1.1.

        Examples:
        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt | # single file                    |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               | # multiple files with wild cards |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/  |  0777  | CRLF | # file permissions and forcing Windows newlines |

        """
        cmd = self.ssh_client.put_file
        return self._run_sftp_command(cmd, source, destination, mode, newline,
                                      path_separator)

    def _run_sftp_command(self, command, *args):
        try:
            sources, destinations = command(*args)
        except SSHClientException, e:
            raise RuntimeError(e)
        for src, dst in zip(sources, destinations):
            self._info("'%s' -> '%s'" % (src, dst))

    def _info(self, msg):
        self._log(msg, 'INFO')

    def _debug(self, msg):
        self._log(msg, 'DEBUG')

    def _log(self, msg, level=None):
        level = self._active_loglevel(level)
        msg = msg.strip()
        if msg:
            print '*%s* %s' % (level, msg)

    def _active_loglevel(self, level):
        if level is None:
            return self._config.loglevel
        if isinstance(level, basestring) and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN', 'HTML']:
            return level.upper()
        raise AssertionError("Invalid log level '%s'" % level)


class DefaultConfig(Configuration):

    def __init__(self, timeout, newline, prompt, loglevel, encoding):
        Configuration.__init__(self,
                timeout=TimeEntry(timeout or 3),
                newline=NewlineEntry(newline or 'LF'),
                prompt=StringEntry(prompt),
                loglevel=LogLevelEntry(loglevel or 'INFO'),
                encoding=StringEntry(encoding or 'UTF-8'))
