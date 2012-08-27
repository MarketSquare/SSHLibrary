from .client import SSHClient, AbstractSSHClient
from .connectioncache import ConnectionCache
from .core import DefaultConfig, ClientConfig, SSHClientException
from .deprecated import DeprecatedSSHLibraryKeywords
from .version import VERSION

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
        timeout = timeout or self._config.timeout
        newline = newline or self._config.newline
        prompt = prompt or self._config.prompt
        config = ClientConfig(host, alias, port, timeout, newline, prompt,
                              term_type, width, height)
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

    def get_connections(self):
        """Return information about opened connections.

        The return value is a list of objects that describe the connection.
        These objects have attributes that correspond to the argument names
        of `Open Connection`.

        Example:
        | Open Connection | somehost  | prompt=>> |
        | Open Connection | otherhost | timeout=5 minutes |
        | ${info} = | Get Connections |
        | Should Be Equal | ${info[0].host} | somehost |
        | Should Be Equal | ${info[1].timeout} | 5 minutes |
        """
        # TODO: could the ConnectionCache be enhanced to be iterable?
        configs = [c.config for c in self._cache._connections]
        for c in configs:
            self._log(str(c))
        return configs

    def enable_ssh_logging(self, logfile):
        """Enables logging of SSH protocol output to given `logfile`

        `logfile` can be relative or absolute path to a file that is writable
        by current user. In case that it already exists, it will be
        overwritten.

        Note that this keyword only works with Python, e.g. when executing the
        tests with `pybot`
        """
        if AbstractSSHClient.enable_logging(logfile):
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
        return self._login(self.ssh_client.login, username, password)

    def login_with_public_key(self, username, keyfile, password):
        """Logs into SSH server with using key-based authentication.

        `username` is the username on the remote system.
        `keyfile` is a path to a valid OpenSSH *private* key file.
        `password` is used to unlock `keyfile` if unlocking is required.

        Reads and returns available output. If prompt is set, everything until
        the prompt is returned.
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
        return self._read_and_log(self.ssh_client.read_until_newline, loglevel)

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
        return self._read_and_log(self.ssh_client.read, loglevel)

    def read_until(self, expected, loglevel=None):
        """Reads output until expected is encountered or timeout expires.

        Text up until and including the match will be returned, If no match is
        found, the keyword fails.

        The timeout is by default three seconds but can be changed either on
        `library importing` or by using `Set Timeout` keyword.

        See `Read` for more information on `loglevel`.
        """
        reader = lambda: self.ssh_client.read_until(expected)
        return self._read_and_log(reader, loglevel)

    def read_until_regexp(self, regexp, loglevel=None):
        """Reads output until a match to `regexp` is found or timeout expires.

        `regexp` can be a pattern or a compiled regexp-object.

        Returns text up until and including the regexp.

        The timeout is by default three seconds but can be changed either on
        `library importing` or by using `Set Timeout` keyword.

        See `Read` for more information on `loglevel`.
        Examples:
        | Read Until Regexp | (#|$) |
        | Read Until Regexp | some regexp  | DEBUG |
        """
        reader = lambda: self.ssh_client.read_until_regexp(regexp)
        return self._read_and_log(reader, loglevel)

    def read_until_prompt(self, loglevel=None):
        """Reads and returns text from the output until prompt is found.

        Prompt must have been set, either in `library importing` or by using
        `Set Prompt` -keyword.

        See `Read` for more information on `loglevel`.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and the command does not
        produce prompt characters in its output.
        """
        return self._read_and_log(self.ssh_client.read_until_prompt, loglevel)

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
        reader = lambda: self.ssh_client.write_until_expected(
                            text, expected, timeout, retry_interval)
        self._read_and_log(reader, loglevel)

    def _read_and_log(self, reader, loglevel):
        try:
            output = reader()
        except SSHClientException, e:
            raise RuntimeError(e)
        self._log(output, loglevel)
        return output

    def get_file(self, source, destination='.'):
        """Copies file(s) from remote host to local host.

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

        Using wild cards like '*' and '?' are allowed in the source.
        When wild cards are used, destination MUST be a directory, and files
        matching the pattern are copied, but sub directories are ignored. If
        the contents of sub directories are also needed, use the keyword again.

        Examples:
        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # single file                    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # multiple files with wild cards |

        """
        return self._run_sftp_command(self.ssh_client.get_file, source,
                                      destination)

    def put_file(self, source, destination='.', mode='0744',
                 newline='default'):
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

        Using wild cards like '*' and '?' are allowed in the source.
        When wild cards are used, destination MUST be a directory and only
        files are copied from the source, sub directories are ignored. If the
        contents of sub directories are also needed, use the keyword again.

        Default file permission is 0744 (-rwxr--r--) and can be changed by
        giving a value to the optional `mode` parameter.

        `newline` can be used to force newline characters that are written to
        the remote file. Valid values are `CRLF` (for Windows) and `LF`.

        Examples:
        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt | # single file                    |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               | # multiple files with wild cards |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/  |  0777  | CRLF | # file permissions and forcing Windows newlines |

        """
        cmd = self.ssh_client.put_file
        return self._run_sftp_command(cmd, source, destination, mode, newline)

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
        level = self._active_log_level(level)
        msg = msg.strip()
        if msg != '':
            print '*%s* %s' % (level, msg)

    def _active_log_level(self, level):
        if level is None:
            return self._config.log_level
        if isinstance(level, basestring) and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN', 'HTML']:
            return level.upper()
        raise AssertionError("Invalid log level '%s'" % level)
