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

plural_or_not = lambda count: '' if count == 1 else 's'


class SSHLibrary(DeprecatedSSHLibraryKeywords):
    """Robot Framework test library for SSH and SFTP.

    SSHLibrary works with both Python and Jython interpreters.

    = Requirements =

    To use SSHLibrary with Python, you must first install Paramiko SSH
    implementation[1]. For Jython, you must have the JAR distribution of
    Trilead SSH implementation[2] in the CLASSPATH during the test execution.

    | [1] https://github.com/paramiko/paramiko
    | [2] http://robotframework-sshlibrary.googlecode.com/files/trilead-ssh2-build213.jar

    = Connections =

    The library supports multiple connections to different hosts.
    New connections are opened with `Open Connection` keyword.

    Only one connection can be active at a time. This means that most of the
    keywords only affect to the active connection. Active connection can be
    changed using `Switch Connection` keyword.

    = Executing commands =

    For executing commands on the remote host, there are two possibilities:

    1. `Execute Command` or `Start Command`. These keywords open a new session
    using the connection. Possible changes to state are not preserved.

    2. Keywords `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
    `Read Command Output`, `Read Until`, `Read Until Prompt` and
    `Read Until Regexp` keywords operate in an interactive shell, which
    means that changes to state are visible to later keywords. Note that in
    interactive mode, prompt must be set before using any of the
    Write-keywords.

    = Configuration =

    Prompt, as well as the other settings can be configured as defaults for
    all the upcoming connections on `library importing` or by using keyword
    `Set Default Configuration`. Settings overriding these defaults
    (except `loglevel`) can be given as arguments to `Open Connection`.

    Currently active, already open connection can be configured with
    `Set Client Configuration`.

    = Pattern matching =

    Some keywords allow their arguments to be specified as _glob patterns_
    where:
    | *        | matches anything, even an empty string |
    | ?        | matches any single character |
    | [chars]  | matches any character inside square brackets (e.g. '[abc]' matches either 'a', 'b' or 'c') |
    | [!chars] | matches any character not inside square brackets |

    Unless otherwise noted, matching is case-insensitive on
    case-insensitive operating systems such as Windows. Pattern
    matching is implemented using
    [http://docs.python.org/library/fnmatch.html|fnmatch module].
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, timeout='3 seconds', newline='LF', prompt=None,
                 loglevel='INFO', encoding='utf8'):
        """SSH Library allows some import time configuration.

        Default settings (except `loglevel`) may later be changed with
        `Set Default Configuration`. Settings of an active,
        already open connection can be changed with `Set Client Configuration`.

        `timeout` is used both by `Read Until` and `Write Until` variants.
        The default is '3 seconds'.

        `newline` is the line break sequence used by the operating system
        on the remote. The default value is 'LF' which is also the default on
        Unix-like operating systems.

        `prompt` is a character sequence that is used by `Read Until Prompt`.
        Prompt must be set before `Read Until Prompt` can be can be used.

        `encoding` is the character encoding of input and output sequences.
        Possible `encoding` values are listed in [3]. Starting from
        SSHLibrary 1.2, the default value is 'UTF-8'.

        | [3] http://docs.python.org/2/library/codecs.html#standard-encodings

        `timeout`, `newline`, `prompt` and `encoding` values set here may
        later be overridden per connection by defining them as arguments
        to `Open Connection`.

        `loglevel` sets the default log level used to log the output read by
        `Read Until` variants. This cannot be configured per connection.
        Possible values are 'TRACE', 'DEBUG', 'INFO' and 'WARN'.
        The default value is 'INFO'.

        Examples that imports the library with sensible defaults:
        | Library | SSHLibrary |

        Example that takes library into use and sets prompt to '>':
        | Library | SSHLibrary | prompt=> |

        Example that takes library into use and changes timeout to 10 seconds
        and changes line breaks to the Windows format:
        | Library | SSHLibrary | timeout=10 seconds | newline=CRLF |
        """
        self._cache = ConnectionCache()
        self._config = DefaultConfig(timeout, newline, prompt, loglevel,
                                     encoding)

    @property
    def ssh_client(self):
        return self._cache.current

    def set_default_configuration(self, timeout=None, newline=None,
                                  prompt=None, loglevel=None, encoding=None):
        """Update the default configuration values set on `library importing`.

        Only parameters whose value is other than `None` are updated.

        Example that updates newline and prompt, but leaves timeout, log level
        and encoding settings intact:
        | Set Default Configuration | newline=CRLF | prompt=$ |
        """
        self._config.update(timeout=timeout, newline=newline, prompt=prompt,
                            loglevel=loglevel, encoding=encoding)

    def set_client_configuration(self, timeout=None, newline=None, prompt=None,
                                 term_type='vt100', width=80, height=24,
                                 encoding=None):
        """Update the active connection configuration values.

        At least one connection must have been opened using `Open Connection`.

        Only parameters whose value is other than `None` are updated.

        Example that updates terminal type and timeout of the currently
        active connection and leaves other connection settings and connections
        intact:
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

        The new connection is made active. Possible existing connections
        are left open in the background.

        This keyword returns the index of this connection which can be used
        later to switch back to it. Indices start from '1' and are reset
        when `Close All Connections` is used.

        Optional `alias` can be given as a name for the connection and can be
        used for switching between connections, similarly as the index.
        See `Switch Connection` for more details.

        If `timeout`, `newline`, `prompt` or `encoding` are not given,
        the default values set on `library importing` or set with
        `Set Default Configuration` are used.

        Starting from SSHLibrary 1.1, a shell session is also opened
        automatically by this keyword.

        `term_type` defines the terminal type for this shell, and `width`
        and `height` can be configured to control the virtual size of it.

        Client configuration options, other than `host`, `port` and `alias`,
        can be later updated with `Set Client Configuration`.

        Examples:
        | Open Connection | myhost.net      |
        | Open Connection | yourhost.com    | alias=2nd conn | port=23 | prompt=# |
        | Open Connection | myhost.net      | term_type=ansi | width=40 |
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
        | Open Connection     | yourhost.com      |
        | # Do something with yourhost.com |      |
        | Close Connection    |                   |
        | Switch Connection   | ${old_connection} |
        """
        return self._cache.current_index

    def switch_connection(self, index_or_alias):
        """Switches the active connection by index or alias.

        `index_or_alias` is either connection index (integer) or explicitly
        defined alias (string) that was given as an argument to
        `Open Connection`.

        Connection index is got as a return value from `Open Connection` or
        from `Get Connection Id`. If `None` is given as argument `index_or_alias`,
        the currently active connection is is closed.

        This keyword returns the index of the previously active connection,
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
        opening the first one. Thus index '1' can be used to switch back to it
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
        """Closes all open connections and empties the connection cache.

        After this keyword, the connection indices returned by `Open Connection`
        are reset and start from 1.

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

        This keyword also logs the connection information. Default log level
        is set either on `library importing` or with
        `Set Default Configuration`.

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
        by the current local user. If the `logfile` already exists, it will be
        overwritten.

        Note that this keyword only works with Python, i.e. when executing
        tests with `pybot`.
        """
        if SSHClient.enable_logging(logfile):
            self._log('SSH log is written to <a href="%s">file</a>.' % logfile,
                      'HTML')

    def close_connection(self):
        """Closes the currently active connection.

        No other connection is made active by this keyword. Manually use
        `Switch Connection` to switch to another connection.
        """
        self.ssh_client.close()
        self._cache.current = self._cache._no_current

    def login(self, username, password):
        """Logs into the SSH server using the given `username` and `password`.

        This keyword also reads and returns the output from the server.
        If prompt is set, everything until the prompt is returned.

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

        This keyword also reads and returns the output from the server.
        If prompt is set, everything until the prompt is returned.
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
        and return code. The command is executed in a new session.

        If several arguments evaluate true, a tuple containing the values
        is returned. `return_stdout`, `return_stderr` and `return_rc`
        can be used to configure whether the tuple contains all these values.
        If only one of the arguments evaluates true, the corresponding value is
        returned instead of a tuple.

        Example that returns only the command stdout as a value:
        | ${stdout}= | Execute Command | ${cmd} |

        Example that returns both stdout and stderr as a tuple:
        | ${stdout} | ${stderr}= | Execute Command | ${cmd} | return_stderr=yes |

        Example that returns only the return code as a value:
        | ${rc}= | Execute Command | ${cmd} | return_stdout=${EMPTY} | return_rc=true |

        This keyword waits until the command execution is finished.
        If non-blocking behavior is required, use `Start Command` instead.

        Multiple calls of `Execute Command` use separate SSH sessions. Thus,
        possible changes to the environment are not shared between these calls.
        `Write` and `Read` keywords can be used for running multiple
        commands in the same session.

        This keyword also logs the executed command with log level 'INFO'.
        """
        self._info("Executing command '%s'" % command)
        opts = self._output_options(return_stdout, return_stderr, return_rc)
        stdout, stderr, rc = self.ssh_client.execute_command(command)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def start_command(self, command):
        """Starts execution of the `command` on the remote host and returns
        immediately.

        This keyword does not return anything. Use `Read Command Output` to read
        the output generated by the command execution.

        Note that the `Read Command Output` keyword always reads the output of
        the most recently started command.

        Example:
        | Start Command | ./myjobscript.sh |

        This keyword also logs the started command with log level 'INFO'.
        """
        self._info("Starting command '%s'" % command)
        self._last_command = command
        self.ssh_client.start_command(command)

    def read_command_output(self, return_stdout=True, return_stderr=False,
                            return_rc=False):
        """Reads output of the most recent started command and returns a
        combination of stdout, stderr and the return code of the command.

        Command must have been started using `Start Command` before this
        keyword can be used.

        See `Execute Command` for examples on how the return value can
        be configured using `return_stdout`, `return_stderr` and `return_rc`.

        This keyword also logs the read command with log level 'INFO'.
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

        Consumes the written `text` (until the appended newline) from the
        server output and returns it. Given `text` must not contain newlines.

        Note: This keyword does not return any output of the executed
        command. To get the output, one of the `Read` keywords must be
        used.

        This keyword logs the written `text` with log level 'INFO'.

        This keyword also logs the read output. Default log level is set
        either on `library importing` or with `Set Default Configuration`.
        `loglevel` can be used to override the default log level.
        Possible levels are 'TRACE', 'DEBUG', 'INFO' and 'WARN'.
        """
        self._write(text, add_newline=True)
        return self._read_and_log(loglevel, self.ssh_client.read_until_newline)

    def write_bare(self, text):
        """Writes the given `text` over the connection without appending
        a newline.

        Unlike `Write`, this keyword does not consume the written text from
        the server output.

        Note: This keyword does not return any output of the executed
        command. To get the output, one of the `Read` keywords must be
        used.

        This keyword logs the written `text` with log level 'INFO'.
        """
        self._write(text)

    def _write(self, text, add_newline=False):
        self._info("Writing %s" % text)
        try:
            self.ssh_client.write(text, add_newline)
        except SSHClientException, e:
            raise RuntimeError(e)

    def read(self, loglevel=None):
        """Reads and returns everything currently available on the
        server output.

        This keyword is most useful for reading everything from the output.
        After being read, the output buffer is cleared.

        This keyword logs the read output. Default log level is set
        either on `library importing` or with `Set Default Configuration`.
        `loglevel` can be used to override the default log level.
        Possible levels are 'TRACE', 'DEBUG', 'INFO' and 'WARN'.
        """
        return self._read_and_log(loglevel, self.ssh_client.read)

    def read_until(self, expected, loglevel=None):
        """Reads the server output until the `expected` is encountered or
        timeout expires.

        Text up until and including the `expected` will be returned.
        If no match is found, the keyword fails.

        The timeout is three seconds by default. Timeout can be set
        either on `library importing', with `Set Default Configuration` or
        as an argument to `Open Connection`. For active connection,
        `Set Client Configuration` can be used.

        This keyword logs the read output. See `Read` for more information
        on `loglevel`.
        """
        return self._read_and_log(loglevel, self.ssh_client.read_until,
                                  expected)

    def read_until_regexp(self, regexp, loglevel=None):
        """Reads output until a match to `regexp` is found or timeout expires.

        `regexp` can be a pattern or a compiled regexp object.

        Returns text up until and including the `regexp.

        The timeout is three seconds by default. Timeout can be set
        either on `library importing', with `Set Default Configuration` or
        as an argument to `Open Connection`. For currently active connection,
        `Set Client Configuration` can be used.

        This keyword logs the read output. See `Read` for more information
        on `loglevel`.

        Example:
        | Read Until Regexp | (#|$) |

        Example that logs the read output with log level DEBUG:
        | Read Until Regexp | some regexp  | DEBUG |
        """
        return self._read_and_log(loglevel, self.ssh_client.read_until_regexp,
                                  regexp)

    def read_until_prompt(self, loglevel=None):
        """Reads and returns text from the output until the prompt is found.

        Prompt must have been set before this keyword. Prompt can be set
        either on `library importing', with `Set Default Configuration` or
        as an argument to `Open Connection`. For currently active connection,
        `Set Client Configuration` can be used.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and the command does not
        produce prompt characters in its output.

        This keyword logs the read output. See `Read` for more information
        on `loglevel`.
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

        This keyword logs the read output. See `Read` for more information
        on `loglevel`.

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
        """Downloads file(s) from the remote host to the local host.

        `source` is a path on the remote machine. Relative or absolute
        path may be used.

        `destination` is the target path on the local machine. Relative or
        absolute path may be used.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-Likes, this is '/' which is also
        the default value. With Windows remotes, this must be set as '\\'.
        This option was added in SSHLibrary 1.1.

        1. If `destination` is an existing file, `source` file is downloaded
           over it.
        2. If `destination` is an existing directory, `source` file is
           downloaded into it. Possible file with the same name is overwritten.
        3. If `destination` does not exist and it ends with `path_
           separator`, it is considered a directory. The directory is then
           created and `source` file is downloaded into it. Possible missing
           intermediate directories are also created.
        4. If `destination` does not exist and does not end with
           `path_separator`, it is considered a file. If the path to the file
           does not exist, it is created.
        5. If `destination` is not given, the current working directory on
           the local machine is used as the destination. This will most probably
           be the directory where the test execution was started.

        Using wildcards is possible in `source`. The pattern matching syntax
        is explained in `pattern matching`. When wildcards are used,
        `destination` MUST be a directory, and files matching the pattern are
        downloaded, but subdirectories are ignored.

        Examples:
        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # single file                    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # all text files by using wildcards |
        """
        return self._run_sftp_command(self.ssh_client.get_file, source,
                                      destination, path_separator)

    def get_directory(self, source, destination='.', path_separator='/',
                      recursive=False):
        """Downloads a directory, including it's content, from the remote host
        to the local host.

        `source` is a path on the remote machine. Relative or absolute
        path may be used.

        `destination` is the target path on the local machine. Relative or
        absolute path may be used.

        1. If `destination` is an existing path on the local machine,
           `source` directory is downloaded into it.

           In this example, remote `source`, '/var/logs', is downloaded into
           an existing local `destination` '/home/robot':
           | Get Directory | /var/logs | /home/robot |

           As a result, the content of remote directory '/var/logs' is now
           found at '/home/robot/logs'. Subdirectories are not included.

        2. If `destination` is a non-existing path on the local machine,
           the local path is created and the content of `source` directory is
           downloaded into it.

           In this example, the content of the remote `source`,
           directory 'logs', in downloaded to a non-existing local
           `destination` 'my_new_path':
           | Get Directory | logs | my_new_path |

           Note the use of relative paths in both `source` and `destination`.

           Because 'my_new_path' does not already exist on the local machine,
           it is created. As the result of keyword, 'my_new_path' now has the
           same content as the remote directory 'logs' but not the 'logs'
           directory itself. Subdirectories are not included.

        3. If `destination` is not given, `source` directory is downloaded into
           the current working directory on the local machine.
           This will most probably be the directory where the test execution
           was started.

           In this example, `source` is downloaded into the current working
           directory:
           | Get Directory | /path/to/remote/logs |

           Note the missing `destination`. It is also possible to refer
           to the current working directory by using '.'. This works both on
           the local and the remote side.

           In this case, `destination` always exists. As a result,
           the remote directory 'logs' can be now found at the current
           working directory by name 'logs'. Subdirectories are not included.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-Likes, this must be '/' which is also
        the default value. With Windows remotes, this must be set as '\\':
        This option was added in SSHLibrary 1.1.

        `recursive` specifies, whether to recursively download all
        subdirectories inside `source`. Subdirectories are downloaded if
        the argument value evaluates to 'True'. The default value is 'False'.

        The following example is identical to (1.), but also the subdirectories
        (and subdirectories of the subdirectories, ad infinitum) inside
        `source`, '/var/logs', are downloaded:
        | Get Directory | /var/logs | /home/robot | recursive=True |

        As a result, the content of the remote directory '/var/logs',
        including it's subdirectories, is now found at '/home/robot/logs'.
        Subdirectory paths are preserved, e.g. remote 'var/logs/mysql'
        is now found at '/home/robot/logs/mysql'.
        """
        return self._run_sftp_command(self.ssh_client.get_directory, source,
                                      destination, path_separator, recursive)

    def put_file(self, source, destination='.', mode='0744',
                 newline='default', path_separator='/'):
        """Uploads file(s) from the local host to the remote host.

        `source` is the path on the local machine. Relative or absolute
        path may be used.

        `destination` is the target path on the remote machine. Relative or
        absolute path may be used.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-Likes, this is '/' which is also
        the default value. With Windows remotes, this must be set as '\\'.
        This option was added in SSHLibrary 1.1.

        `mode` argument can be used to set the target file permission.
        Numeric values are accepted. The default value is '0744' (-rwxr--r--).

        `newline` can be used to force newline characters that are written to
        the remote file. Valid values are `CRLF` (for Windows) and `LF`.

        1. If `destination` is an existing file, `source` file is uploaded
           over it.
        2. If `destination` is an existing directory, `source` file is
           uploaded into it. Possible file with same name is overwritten.
        3. If `destination` does not exist and it ends with `path_
           separator`, it is considered a directory. The directory is then
           created and `source` file uploaded into it. Possibly missing
           intermediate directories are also created.
        4. If `destination` does not exist and it does not end with
           `path_separator, it is considered a file. If the path to the file
           does not exist, it is created.
        5. If `destination` is not given, the user's home directory
           on the remote is used as the destination.

        Using wildcards is possible in `source`. The pattern matching syntax
        is explained in `pattern matching`. When wildcards are used,
        `destination` MUST be a directory and only files are uploaded from
        source, subdirectories being ignored.

        Examples:
        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt | # single file                    |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               | # all text files by using wildcards |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/  |  0777  | CRLF | # file permissions and forcing Windows newlines |
        """
        return self._run_sftp_command(self.ssh_client.put_file, source,
                                      destination, mode, newline,
                                      path_separator)

    def put_directory(self, source, destination='.', mode='0744',
                      newline='default', path_separator='/', recursive=False):

        """Uploads a directory, including it's content, from the local host
        to the remote host.

        `source` is the path on the local machine. Relative or absolute
        path may be used.

        `destination` is the target path on the remote machine. Relative or
        absolute path may be used.

        1. If `destination` is an existing path on the remote,
           `source` directory is uploaded into it.

           In this example, local `source`, '/var/logs', is uploaded into
           an already existing remote `destination` '/home/robot':
           | Put Directory | /var/logs | /home/robot |

           As a result, the content of local directory '/var/logs' is now
           found on the remote at '/home/robot/logs'. Subdirectories are not
           included.

        2. If `destination` is a non-existing path on the remote, it is created
           and the content of `source` directory is uploaded into it.

           In this example, the content of the local `source` directory 'logs',
           in the current working directory, is uploaded to a non-existing
           remote `destination` 'my_new_path':
           | Put Directory | logs | my_new_path |

           Note the use of relative paths in both `source` and `destination`.

           Because 'my_new_path' does not already exist on the remote,
           it is created. As the result of keyword, 'my_new_path' now has the
           same content as the local directory 'logs' but not the 'logs'
           directory itself. Subdirectories are not included.

        3. If `destination` is not given, `source` directory is uploaded into
           the current working directory on the remote.

           In this example, `source` is uploaded into the current working
           directory on the remote:
           | Put Directory | /path/to/remote/logs |

           Note the missing `destination`. It is also possible to refer
           to the current working directory by using '.'. This works both on
           the local and the remote side.

           In this case, `destination` always exists. As a result,
           the local directory 'logs' is now found at the current remote
           working directory by name 'logs'. Subdirectories are not included.

        `mode` argument can be used to set the file permissions.
        Numeric values are accepted. The default value is '0744' (-rwxr--r--).

        `newline` can be used to force newline characters that are written to
        the remote files. Valid values are `CRLF` (for Windows) and `LF`.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-Likes, this must be '/' which is also
        the default value. With Windows remotes, this must be set as '\\':
        This option was added in SSHLibrary 1.1.

        `recursive` specifies, whether to recursively upload all
        subdirectories inside `source`. Subdirectories are uploaded if the
        argument value evaluates to 'True'. The default value is 'False'.

        The following example is identical to (1.), but also the subdirectories
        (and subdirectories of the subdirectories, ad infinitum) inside
        `source`, '/var/logs', are uploaded:
        | Put Directory | /var/logs | /home/robot | recursive=True |

        As a result, the content of the local directory '/var/logs',
        including it's subdirectories, is now found on the remote at
        '/home/robot/logs'. Subdirectory paths are preserved, e.g.
        local 'var/logs/mysql' is found on the remote
        at '/home/robot/logs/mysql'.
        """
        return self._run_sftp_command(self.ssh_client.put_directory, source,
                                      destination, mode, newline,
                                      path_separator, recursive)

    def list_directory(self, path, pattern=None, absolute=False):
        """Returns and logs items in a remote directory, optionally filtered
        with `pattern`.

        File and directory names are returned in case-sensitive alphabetical
        order, e.g. ['A Name', 'Second', 'a lower case name', 'one more'].
        Implicit directories '.' and '..' are not returned. The returned items
        are automatically logged.

        By default, the file and directory names are returned relative to the
        given remote path (e.g. 'file.txt'). If you want them be returned in the
        absolute format (e.g. '/home/robot/file.txt'), set the `absolute`
        argument to any non-empty string.

        If `pattern` is given, only items matching it are returned. The pattern
        matching syntax is explained in `introduction`, and in this case
        matching is case-sensitive.

        Examples (using also other `List Directory` variants):
        | @{items} = | List Directory           | /home/robot |
        | @{files} = | List Files In Directory  | /tmp | *.txt | absolute=True |
        """
        items = self.ssh_client.list_dir(path, pattern, absolute)
        self._info('%d item%s:\n%s' % (len(items), plural_or_not(items), '\n'.join(items)))
        return items

    def list_files_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only files."""
        files = self.ssh_client.list_files_in_dir(path, pattern, absolute)
        self._info('%d file%s:\n%s' % (len(files), plural_or_not(files), '\n'.join(files)))
        return files

    def list_directories_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only directories."""
        dirs = self.ssh_client.list_dirs_in_dir(path, pattern, absolute)
        self._info('%d director%s:\n%s' % (len(dirs), 'y' if len(dirs) == 1 else 'ies', '\n'.join(dirs)))
        return dirs

    def directory_should_exist(self, path):
        """Fails if the given path does not point to an existing directory.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `pattern matching`.
        """
        return self.ssh_client.dir_exists(path)

    def directory_should_not_exist(self, path):
        """Fails if the given path points to an existing directory.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `pattern matching`.
        """
        return not self.ssh_client.dir_exists(path)

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
                timeout=TimeEntry(timeout or '3 seconds'),
                newline=NewlineEntry(newline or 'LF'),
                prompt=StringEntry(prompt),
                loglevel=LogLevelEntry(loglevel or 'INFO'),
                encoding=StringEntry(encoding or 'utf8'))
