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
from config import (Configuration, IntegerEntry, LogLevelEntry, NewlineEntry,
                    StringEntry, TimeEntry)
from .version import VERSION

__version__ = VERSION

plural_or_not = lambda count: '' if count == 1 else 's'


class SSHLibrary(object):
    """Robot Framework test library for SSH and SFTP.

    The library has the following main usages:
    - Executing commands on the remote machine, either with blocking or
      non-blocking behaviour (`Execute Command` and `Start Command`,
      respectively).
    - Writing and reading in an interactive shell (e.g. `Read` and `Write`)
    - Transferring files and directories over SFTP (e.g. `Get File` and
      `Put Directory`).
    - Ensuring that files or directories exist on the remote machine
      (e.g. `File Should Exist` and `Directory Should Not Exist`).

    == Table of contents ==

    - `Connections and login`
    - `Configuration`
    - `Executing commands`
    - `Pattern matching`
    - `Example`
    - `Importing`
    - `Shortcuts`
    - `Keywords`

    = Connections and login =

    The library supports multiple connections to different hosts.
    New connections are opened with `Open Connection`.

    Logging into the host is done either with username and password
    (`Login`) or with public/private key pair (`Login With Public key`).

    Only one connection can be active at a time. This means that most of the
    keywords only affect the active connection. Active connection can be
    changed with `Switch Connection`.

    = Configuration =

    Default settings for all the upcoming connections can be configured on
    `library importing` or later with `Set Default Configuration`.
    All the settings are listed further below.

    Using `Set Default Configuration` does not affect the already open
    connections. Settings of the current connection can be configured
    with `Set Client Configuration`. Settings of another, non-active connection,
    can be configured by first using `Switch Connection` and then
    `Set Client Configuration`.

    Most of the defaults can be overridden per connection by defining them
    as arguments to `Open Connection`. Otherwise the defaults are used.

    == Configurable per connection ==

    === Default timeout ===

    Timeout is used by `Read Until` variants. The default value is `3 seconds`.

    Value must be in Robot Framework's time format, e.g. `3`, `4.5`, `1 minute`
    and `2 min 3 s` are all accepted. See section 'Time Format' in
    Robot Framework User Guide for details.

    === Default newline ===

    Newline is the line break sequence known by the operating system
    on the remote machine. The default value is `LF` which is used by
    Unix-like operating systems.

    === Default prompt ===

    Prompt is a character sequence used by `Read Until Prompt`
    and must be set before the keyword can be used.

    === Default terminal settings ===

    Argument `term_type` defines the terminal type on the remote machine and
    arguments `width` and `height` can be used to set the virtual size of it.

    === Default encoding ===

    Encoding is the
    [http://docs.python.org/2/library/codecs.html#standard-encodings|character encoding]
    of input and output sequences. Starting from SSHLibrary 1.2, the default
    value is `UTF-8`.

    == Not configurable per connection ==

    === Default loglevel ===

    Loglevel sets the log level used to log the output read by `Read`,
    `Read Until`, `Read Until Prompt`, `Read Until Regexp`, `Write`,
    `Write Until Expected Output` and `Get Connections`. The default level is
    `INFO`. `loglevel` is not configurable per connection but can be overridden
    by passing it as an argument to any of the mentioned keywords.
    Possible values are `TRACE`, `DEBUG`, `INFO` and `WARN`.

    = Executing commands =

    For executing commands on the remote machine, there are two possibilities:

    1. `Execute Command` and `Start Command`. The command is executed in a new
    shell on the remote machine, which means that possible changes to
    the environment (e.g. setting environment variables, changing
    working directory, etc.) are not visible to the subsequent keywords.

    2. `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
    `Read Until`, `Read Until Prompt` and `Read Until Regexp` operate
    in an interactive shell, which means that changes to the environment
    are visible to the subsequent keywords.

    = Interactive shells =

    `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
    `Read Until`, `Read Until Prompt` and `Read Until Regexp` can be used
    to interact with the server within the same shell.

    All of these keywords, except `Write Bare`, consume the read or the written
    text from the server output before returning. In practice, this means that
    the text is removed from the server output, i.e. subsequent calls to
    `Read` keywords do not return text that was already read:
    | Write              | echo 'hello' |       | # consumed: echo 'hello'                           |
    | ${stdout}=         | Read Until   | hello | # consumed: the printed 'hello'                    |
    | Should Contain     | ${stdout}    | hello |
    | ${stdout}=         | Read         |       | # consumed: everything available                   |
    | Should Not Contain | ${stdout}    | hello | # because the printed 'hello' was already consumed |

    The consumed text is logged by the keywords and argument `loglevel`
    can be used to override [#Default loglevel|the default log level].

    `Login` and `Login With Public Key` consume everything on
    the server output or if [#Default prompt|prompt is set], everything until
    the prompt.

    == Reading ==

    `Read`, `Read Until`, `Read Until Prompt` and `Read Until
    Regexp` can be used to read from the server. The read text is also
    consumed from the server output.

    `Read Until` variants read output up until and *including* `expected` text.
    These keywords will fail if [#Default timeout|the timeout] expires before
    `expected` is found.

    == Writing ==

    `Write`, `Write Until Expected Output` consume the written text
    while `Write Bare` does not.

    Any of these keywords does not return output triggered by the written text.
    To get the output, one of the `Read` keywords must be explicitly used.

    = Pattern matching =

    Some keywords allow their arguments to be specified as _glob patterns_
    where:
    | *        | matches anything, even an empty string |
    | ?        | matches any single character |
    | [chars]  | matches any character inside square brackets (e.g. `[abc]` matches either `a`, `b` or `c`) |
    | [!chars] | matches any character not inside square brackets |

    Unless otherwise noted, matching is case-insensitive on case-insensitive
    operating systems such as Windows. Pattern matching is implemented using
    [http://docs.python.org/library/fnmatch.html|fnmatch module].

    = Example =
    | ***** Settings *****
    | Documentation          This example demonstrates executing commands on a remote machine
    | ...                    and getting their output and return code.
    | ...
    | ...                    Notice how connections are handled as part of the suite setup and
    | ...                    teardown. This saves some time when executing several test cases.
    |
    | Library                SSHLibrary
    | Suite Setup            Open Connection And Log In
    | Suite Teardown         `Close All Connections`
    |
    | ***** Variables *****
    | ${HOST}                localhost
    | ${USERNAME}            test
    | ${PASSWORD}            test
    |
    | ***** Test Cases *****
    | Execute Command And Verify Output
    |     [Documentation]    `Execute Command` can be used to ran commands on the remote machine.
    |     ...                The keyword returns the standard output by default.
    |     ${output}=         `Execute Command`   echo Hello SSHLibrary!
    |     Should Be Equal    ${output}         Hello SSHLibrary!
    |
    | Execute Command And Verify Return Code
    |     [Documentation]    Usually getting the return code of the command is enough.
    |     ...                This behaviour can be adjusted as `Execute Command` arguments.
    |     ${rc}=             `Execute Command`   echo Success quaranteed.    return_stdout=False    return_rc=True
    |     Should Be Equal    ${rc}             ${0}
    |
    | Executing Commands In An Interactive Session
    |     [Documentation]    Execute Command always executes the command in a new shell.
    |     ...                This means that changes to the environment are not persisted
    |     ...                between subsequent Execute Command keyword calls.
    |     ...                Write and Read keyword variants can be used to operate in the same shell.
    |                        Write  cd ..
    |                        Write  echo Hello from the parent directory!
    |     ${output}=         Read Until  directory!
    |     Should Contain     ${output}  Hello from the parent directory!
    |
    | ***** Keywords *****
    | Open Connection And Log In
    |    `Open Connection`     ${HOST}
    |    `Login`               ${USERNAME}       ${PASSWORD}

    Save the content as file `executing_command.txt` and run:

    | pybot executing_commands.txt

    You may want to override the variables from commandline to try this out on your remote machine:

    | pybot -v HOST:my.server.com -v USERNAME:johndoe -v PASSWORD:secretpasswd executing_commands.txt
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    DEFAULT_TIMEOUT = '3 seconds'
    DEFAULT_NEWLINE = 'LF'
    DEFAULT_PROMPT = None
    DEFAULT_LOGLEVEL = 'INFO'
    DEFAULT_TERM_TYPE = 'vt100'
    DEFAULT_TERM_WIDTH = 80
    DEFAULT_TERM_HEIGHT = 24
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self,
                 timeout=DEFAULT_TIMEOUT,
                 newline=DEFAULT_NEWLINE,
                 prompt=DEFAULT_PROMPT,
                 loglevel=DEFAULT_LOGLEVEL,
                 term_type=DEFAULT_TERM_TYPE,
                 width=DEFAULT_TERM_WIDTH,
                 height=DEFAULT_TERM_HEIGHT,
                 encoding=DEFAULT_ENCODING):
        """SSHLibrary allows some import time `configuration`.

        If the library is imported without any arguments, the library
        defaults are used:
        | Library | SSHLibrary |

        Only arguments that are given are changed. In this example, the timeout
        is changed to 10 seconds but other settings are left to the library
        defaults:
        | Library | SSHLibrary | 10 seconds |

        Prompt does not have a default value and must be explicitly set to
        use `Read Until Prompt`. In this example, prompt is set to `$`:
        | Library | SSHLibrary | prompt=$ |

        Multiple settings are possible. In this example, the library is brought
        into use with the timeout of 10 seconds and line breaks known by
        Windows:
        | Library | SSHLibrary | 10 seconds | CRLF |

        Arguments `term_type`, `width`, `height` and `encoding` were added
        in SSHLibrary 1.2.
        """
        self._connections = ConnectionCache()
        self._config = _DefaultConfiguration(timeout or self.DEFAULT_TIMEOUT,
                                             newline or self.DEFAULT_NEWLINE,
                                             prompt or self.DEFAULT_PROMPT,
                                             loglevel or self.DEFAULT_LOGLEVEL,
                                             term_type or self.DEFAULT_TERM_TYPE,
                                             width or self.DEFAULT_TERM_WIDTH,
                                             height or self.DEFAULT_TERM_HEIGHT,
                                             encoding or self.DEFAULT_ENCODING)

    @property
    def current(self):
        return self._connections.current

    def set_default_configuration(self, timeout=None, newline=None, prompt=None,
                                  loglevel=None, term_type=None, width=None,
                                  height=None, encoding=None):
        """Update the default `configuration`.

        Please note that using this keyword does not affect the already
        open connections. Use `Set Client Configuration` to configure the
        active connection.

        Only parameters whose value is other than `None` are updated.

        This example sets the prompt to `$`:
        | Set Default Configuration | prompt=$ |

        This example sets `newline` and `loglevel`, but leaves the other
        settings intact:
        | Set Default Configuration | newline=CRLF | loglevel=WARN |

        Sometimes you might want to use longer timeout for all the subsequent
        connections without affecting the existing ones:
        | Set Default Configuration   | timeout=5 seconds  |
        | Open Connection             | local.server.com   |
        | Set Default Configuration   | timeout=20 seconds |
        | Open Connection             | emea.server.com    |
        | Open Connection             | apac.server.com    |
        | ${local}  ${emea}  ${apac}= | Get Connections    |
        | Should Be Equal As Integers | ${local.timeout}   | 5  |
        | Should Be Equal As Integers | ${emea.timeout}    | 20 |
        | Should Be Equal As Integers | ${apac.timeout}    | 20 |

        Arguments `term_type`, `width`, `height` and `encoding` were added
        in SSHLibrary 1.2.
        """
        self._config.update(timeout=timeout, newline=newline, prompt=prompt,
                            loglevel=loglevel, term_type=term_type, width=width,
                            height=height, encoding=encoding)

    def set_client_configuration(self, timeout=None, newline=None, prompt=None,
                                 term_type=None, width=None, height=None,
                                 encoding=None):
        """Update the `configuration` of the current connection.
        At least one connection must have been opened using `Open Connection`.

        Only parameters whose value is other than `None` are updated.

        In the following example, `prompt` is set for the current connection.
        Other settings are left intact:
        | Open Connection          | my.server.com      |
        | Set Client Configuration | prompt=$           |
        | ${myserver}=             | Get Connection     |
        | Should Be Equal          | ${myserver.prompt} | $ |

        Using keyword does not affect to the other connections:
        | Open Connection          | linux.server.com   |   |
        | Set Client Configuration | prompt=$           |   | # Only linux.server.com affected    |
        | Open Connection          | windows.server.com |   |
        | Set Client Configuration | prompt=>           |   | # Only windows.server.com affected  |
        | ${linux}  ${windows}=    | Get Connections    |
        | Should Be Equal          | ${linux.prompt}    | $ |
        | Should Be Equal          | ${windows.prompt}  | > |

        Multiple settings are possible. This example updates both terminal type
        and terminal width of the current connection:
        | Open Connection          | 192.168.1.1    |
        | Set Client Configuration | term_type=ansi | width=40 |

        Argument `encoding` was added in SSHLibrary 1.2.
        """
        self.current.config.update(timeout=timeout, newline=newline,
                                   prompt=prompt, term_type=term_type,
                                   width=width, height=height,
                                   encoding=encoding)

    def enable_ssh_logging(self, logfile):
        """Enables logging of SSH protocol output to given `logfile`.

        All the existing and upcoming connections are logged onwards from
        the moment the keyword was called.

        `logfile` can be relative or absolute path to a file that is writable
        by the current local user. If the `logfile` already exists, it will be
        overwritten.

        Note that this keyword only works with Python, i.e. when executing
        tests with `pybot`.

        Example:
        | Open Connection    | my.server.com   | # Not logged |
        | Enable SSH Logging | myserver.log    |
        | Login              | johndoe         | secretpasswd |
        | Open Connection    | build.local.net | # Logged     |
        | # Do something with the connections  |
        | # Check myserver.log for detailed debug information |
        """
        if SSHClient.enable_logging(logfile):
            self._log('SSH log is written to <a href="%s">file</a>.' % logfile,
                      'HTML')

    def open_connection(self, host, alias=None, port=22, timeout=None,
                        newline=None, prompt=None, term_type=None, width=None,
                        height=None, encoding=None):
        """Opens a new SSH connection to given `host` and `port`.

        The new connection is made active. Possible existing connections
        are left open in the background.

        This keyword returns the index of this connection which can be used
        later to switch back to it. Indices start from `1` and are reset
        when `Close All Connections` is used.

        Optional `alias` can be given as a name for the connection and can be
        used for switching between connections, similarly as the index.
        See `Switch Connection` for more details.

        Connection parameters, like `timeout` and `newline` are documented in
        `configuration`. All the arguments, except `host`, `alias` and `port`
        can be later updated with `Set Client Configuration`.

        Starting from SSHLibrary 1.1, a shell is automatically opened
        by this keyword.

        Port `22` is assumed by default:
        | ${index}= | Open Connection | my.server.com |

        Non-standard port may be given as an argument:
        | ${index}= | Open Connection | 192.168.1.1 | port=23 |

        Aliases are handy, if you need to switch back to the connection later:
        | Open Connection   | my.server.com | alias=myserver |
        | # Do something with my.server.com |
        | Open Connection   | 192.168.1.1   |
        | Switch Connection | myserver      |                | # Back to my.server.com |

        Settings can be overridden per connection, otherwise the ones set on
        `library importing` or with `Set Default Configuration` are used:
        | Open Connection | 192.168.1.1   | timeout=1 hour    | newline=CRLF          |
        | # Do something with the connection                  |
        | Open Connection | my.server.com | # Default timeout | # Default line breaks |

        Terminal settings are also configurable per connection:
        | Open Connection | 192.168.1.1  | term_type=ansi | width=40 |

        Argument `encoding` was added in SSHLibrary 1.2.
        """
        timeout = timeout or self._config.timeout
        newline = newline or self._config.newline
        prompt = prompt or self._config.prompt
        term_type = term_type or self._config.term_type
        width = width or self._config.width
        height = height or self._config.height
        encoding = encoding or self._config.encoding
        client = SSHClient(host, alias, port, timeout, newline, prompt,
                           term_type, width, height, encoding)
        connection_index = self._connections.register(client, alias)
        client.config.update(index=connection_index)
        return connection_index

    def switch_connection(self, index_or_alias):
        """Switches the active connection by index or alias.

        `index_or_alias` is either connection index (an integer) or alias
        (a string). Index is got as the return value of `Open Connection`.
        Alternatively, both index and alias can queried as attributes
        of the object returned by `Get Connection`.

        This keyword returns the index of the previous active connection,
        which can be used to switch back to that connection later.

        Example:
        | ${myserver}=      | Open Connection | my.server.com |
        | Login             | johndoe         | secretpasswd  |
        | Open Connection   | build.local.net | alias=Build   |
        | Login             | jenkins         | jenkins       |
        | Switch Connection | ${myserver}     |               | # Switch using index          |
        | ${username}=      | Execute Command | whoami        | # Executed on my.server.com   |
        | Should Be Equal   | ${username}     | johndoe       |
        | Switch Connection | Build           |               | # Switch using alias          |
        | ${username}=      | Execute Command | whoami        | # Executed on build.local.net |
        | Should Be Equal   | ${username}     | jenkins       |
        """
        old_index = self._connections.current_index
        if index_or_alias is None:
            self.close_connection()
        else:
            self._connections.switch(index_or_alias)
        return old_index

    def close_connection(self):
        """Closes the current connection.

        No other connection is made active by this keyword. Manually use
        `Switch Connection` to switch to another connection.

        Example:
        | Open Connection  | my.server.com  |
        | Login            | johndoe        | secretpasswd |
        | Get File         | results.txt    | /tmp         |
        | Close Connection |
        | # Do something with /tmp/results.txt             |
        """
        self.current.close()
        self._connections.current = self._connections._no_current

    def close_all_connections(self):
        """Closes all open connections.

        After this keyword, the connection indices returned by `Open Connection`
        are reset and start from `1`.

        This keyword is ought to be used either in test or suite teardown to
        make sure all the connections are closed before the test execution
        finishes.

        Example:
        | Open Connection | my.server.com         |
        | Open Connection | build.local.net       |
        | # Do something with the connections     |
        | [Teardown]      | Close all connections |
        """
        self._connections.close_all()

    def get_connection(self, index_or_alias=None, loglevel=None):
        """Return information of the connection by index or alias.

        Connection is not changed by this keyword, use `Switch Connection` to
        change the active connection.

        If `index_or_alias` is not given, the information of the current
        active connection is returned.

        This keyword returns an object that describes the connection.
        The object has attributes that correspond to the [#Configurable
        per connection|connection configuration values] including
        attributes `host`, `port`, `index` and `alias`. If you want
        the objects for all the open connections, use `Get Connections`.

        This keyword logs the connection information. `loglevel` can be used to
        override the [#Default loglevel|default log level].

        Getting information of the current connection:
        | Open Connection | far.server.com        |
        | Open Connection | near.server.com       | prompt=>>       | # Current connection |
        | ${nearhost}=    | Get Connection        |                 |
        | Should Be Equal | ${nearhost.host}      | near.server.com |
        | Should Be Equal | ${nearhost.index}     | 2               |
        | Should Be Equal | ${nearhost.prompt}    | >>              |
        | Should Be Equal | ${nearhost.term_type} | vt100           | # From defaults      |

        Getting connection information using an index:
        | Open Connection | far.server.com   |
        | Open Connection | near.server.com  | # Current connection |
        | ${farhost}=     | Get Connection   | 1                    |
        | Should Be Equal | ${farhost.host}  | far.server.com       |

        Getting connection information using an alias:
        | Open Connection | far.server.com   | alias=far            |
        | Open Connection | near.server.com  | # Current connection |
        | ${farhost}=     | Get Connection   | far                  |
        | Should Be Equal | ${farhost.host}  | far.server.com       |
        | Should Be Equal | ${farhost.alias} | far                  |

        New in SSHLibrary 1.2.
        """
        if not index_or_alias:
            index_or_alias = self._connections.current_index
        config = self._connections.get_connection(index_or_alias).config
        self._log(str(config), loglevel)
        return config

    def get_connections(self, loglevel=None):
        """Return information about all the open connections.

        This keyword returns a list of objects similar to what is returned
        by `Get Connection`. These objects have attributes that correspond
        to the [#Configurable per connection|connection configuration values]
        including attributes `host`, `port`, `index` and `alias`.

        This keyword logs the connection information. `loglevel` can be used to
        override the [#Default loglevel|default log level].

        Example:
        | Open Connection             | near.server.com     | timeout=10s     |
        | Open Connection             | far.server.com      | timeout=5s      |
        | ${nearhost}                 | ${farhost}=         | Get Connections |
        | Should Be Equal             | ${nearhost.host}    | near.server.com |
        | Should Be Equal As Integers | ${nearhost.timeout} | 10              |
        | Should Be Equal As Integers | ${farhost.port}     | 22              |
        | Should Be Equal As Integers | ${farhost.timeout}  | 5               |

        Argument `loglevel` was added in SSHLibrary 1.2.
        """
        configs = [c.config for c in self._connections._connections]
        for c in configs:
            self._log(str(c), loglevel)
        return configs

    def login(self, username, password):
        """Logs into the SSH server with the given `username` and `password`.

        Connection must be opened before using this keyword.

        This keyword returns and consumes everything on the server output
        (usually the server MOTD). If [#Default prompt|prompt is set], everything
        until the prompt is returned and consumed.

        Example that logs in and returns the output:
        | Open Connection | linux.server.com |
        | ${output}=      | Login            | johndoe       | secretpasswd |
        | Should Contain  | ${output}        | Last login at |

        Example that logs in and returns everything until the prompt:
        | Open Connection | linux.server.com | prompt=$         |
        | ${output}=      | Login            | johndoe          | secretpasswd |
        | Should Contain  | ${output}        | johndoe@linux:~$ |
        """
        return self._login(self.current.login, username, password)

    def login_with_public_key(self, username, keyfile, password=''):
        """Logs into the SSH server using key-based authentication.

        Connection must be opened before using this keyword.

        `username` is the username on the remote machine.

        `keyfile` is a path to a valid OpenSSH private key file on the local
        filesystem.

        `password` is used to unlock the `keyfile` if unlocking is required.

        This keyword returns and consumes everything on the server output
        (usually the server MOTD). If [#Default prompt|prompt is set],
        everything until the prompt is returned and consumed.

        Example that logs in using a private key and returns the output:
        | Open Connection | linux.server.com      |
        | ${output}=      | Login With Public Key | johndoe       | /home/johndoe/.ssh/id_rsa |
        | Should Contain  | ${motd}               | Last login at |

        Example that requires unlocking the private key:
        | Open Connection       | linux.server.com |
        | Login With Public Key | johndoe          | /home/johndoe/.ssh/id_dsa | keyringpasswd |
        """
        return self._login(self.current.login_with_public_key, username,
                           keyfile, password)

    def _login(self, login_method, username, *args):
        self._info("Logging into '%s:%s' as '%s'."
                   % (self.current.config.host, self.current.config.port,
                      username))
        try:
            return login_method(username, *args)
        except SSHClientException, e:
            raise RuntimeError(e)

    def execute_command(self, command, return_stdout=True, return_stderr=False,
                        return_rc=False):
        """Executes `command` on the remote machine and return its outputs.

        This keyword executes the `command` and returns after the execution
        has been finished. If returning immediately is required,
        use `Start Command` instead.

        By default, only the standard output is returned:
        | ${stdout}=     | Execute Command | echo 'Hello John!' |
        | Should Contain | ${stdout}       | Hello John!        |

        Arguments `return_stdout`, `return_stderr` and `return_rc` are used
        to specify, what is returned by this keyword.
        If several arguments evaluate to true, multiple values are returned.
        Non-empty strings, except `false` and `False`, evaluate to true.

        If errors are needed as well, set the argument value to true:
        | ${stdout}       | ${stderr}= | Execute Command | echo 'Hello John!' | return_stderr=True |
        | Should Be Empty | ${stderr}  |

        Most of the time, checking the return code is enough:
        | ${rc}=                      | Execute Command | echo 'Hello John!' | return_stdout=False | return_rc=True |
        | Should Be Equal As Integers | ${rc}           | 0                  | # succeeded         |

        The command is always executed in a new shell. Thus possible changes
        to the environment (e.g. changing working directory) are not visible
        to the later keywords:
        | ${pwd}=         | Execute Command | pwd           |
        | Should Be Equal | ${pwd}          | /home/johndoe |
        | Execute Command | cd /tmp         |
        | ${pwd}=         | Execute Command | pwd           |
        | Should Be Equal | ${pwd}          | /home/johndoe |

        `Write` and `Read` can be used for
        [#Interactive shells|running subsequent commands in the same shell].

        This keyword also logs the executed command and the exit
        status with log level `INFO`.
        """
        self._info("Executing command '%s'" % command)
        opts = self._legacy_output_options(return_stdout, return_stderr,
                                           return_rc)
        stdout, stderr, rc = self.current.execute_command(command)
        self._info("Command exited with status '%i'" % rc)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def start_command(self, command):
        """Starts execution of the `command` on the remote machine and
        returns immediately.

        This keyword returns nothing and does not wait for the command
        execution to be finished. If waiting for the output is required,
        use `Execute Command` instead.

        This keyword does not return output generated by the started command.
        Use `Read Command Output` to read the output:
        | Start Command   | echo 'Hello John!'  |
        | ${stdout}=      | Read Command Output |
        | Should Contain  | ${stdout}           | Hello John! |

        The command is always executed in a new shell, similarly as with
        `Execute Command`. Thus possible changes to the environment
        (e.g. changing working directory) are not visible to the later keywords:
        | Start Command   | pwd                 |
        | ${pwd}=         | Read Command Output |
        | Should Be Equal | ${pwd}              | /home/johndoe |
        | Start Command   | cd /tmp             |
        | Start Command   | pwd                 |
        | ${pwd}=         | Read Command Output |
        | Should Be Equal | ${pwd}              | /home/johndoe |

        `Write` and `Read` can be used for
        [#Interactive shells|running subsequent commands in the same shell].

        This keyword also logs the started command with log level `INFO`.
        """
        self._info("Starting command '%s'" % command)
        self._last_command = command
        self.current.start_command(command)

    def read_command_output(self, return_stdout=True, return_stderr=False,
                            return_rc=False):
        """Returns outputs of the most recent started command.

        At least one command must have been started using `Start Command`
        before this keyword can be used.

        By default, only the standard output of the started command is returned:
        | Start Command  | echo 'Hello John!'  |
        | ${stdout}=     | Read Command Output |
        | Should Contain | ${stdout}           | Hello John! |

        Arguments `return_stdout`, `return_stderr` and `return_rc` are used
        to specify, what is returned by this keyword.
        If several arguments evaluate to true, multiple values are returned.
        Non-empty strings, except `false` and `False`, evaluate to true.

        If errors are needed as well, set the argument value to true:
        | Start Command   | echo 'Hello John!' |
        | ${stdout}       | ${stderr}=         | Read Command Output | return_stderr=True |
        | Should Be Empty | ${stderr}          |

        Most of the time, checking the return code is enough:
        | Start Command               | echo 'Hello John!'  |
        | ${rc}=                      | Read Command Output | return_stdout=False | return_rc=True |
        | Should Be Equal As Integers | ${rc}               | 0                   | # succeeded         |

        Using `Start Command` and `Read Command Output` follows
        'last in, first out' (LIFO) policy, meaning that `Read Command Output`
        operates on the most recent started command, after which that command
        is discarded and its output cannot be read again.

        If several commands have been started, the output of the last started
        command is returned. After that, a subsequent call will return the
        output of the new last (originally the second last) command:
        | Start Command  | echo 'HELLO'        |
        | Start Command  | echo 'SECOND'       |
        | ${stdout}=     | Read Command Output |
        | Should Contain | ${stdout}           | 'SECOND' |
        | ${stdout}=     | Read Command Output |
        | Should Contain | ${stdout}           | 'HELLO'  |

        This keyword also logs the read command with log level `INFO`.
        """
        self._info("Reading output of command '%s'" % self._last_command)
        opts = self._legacy_output_options(return_stdout, return_stderr,
                                           return_rc)
        try:
            stdout, stderr, rc = self.current.read_command_output()
        except SSHClientException, msg:
            raise RuntimeError(msg)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def _legacy_output_options(self, stdout, stderr, rc):
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
        if self._output_wanted(return_stdout):
            ret.append(stdout.rstrip('\n'))
        if self._output_wanted(return_stderr):
            ret.append(stderr.rstrip('\n'))
        if self._output_wanted(return_rc):
            ret.append(rc)
        if len(ret) == 1:
            return ret[0]
        return ret

    def _output_wanted(self, value):
        return (value and str(value).lower() != 'false')

    def write(self, text, loglevel=None):
        """Writes the given `text` on the remote machine and appends
        [#Default newline|a newline].

        This keyword returns and [#Interactive shells|consumes] the written
        `text` (including the appended newline) from the server output.

        The written `text` is logged with the defined `loglevel`.

        See `interactive shells` for more information on writing.

        Example:
        | ${written}=        | Write         | su                         |
        | Should Contain     | ${written}    | su                         | # Returns the consumed output  |
        | ${output}=         | Read          |
        | Should Not Contain | ${output}     | ${written}                 | # Was consumed from the output |
        | Should Contain     | ${output}     | Password:                  |
        | Write              | invalidpasswd |
        | ${output}=         | Read          |
        | Should Contain     | ${output}     | su: Authentication failure |

        See also `Write Bare`.
        """
        self._write(text, add_newline=True)
        return self._read_and_log(loglevel, self.current.read_until_newline)

    def write_bare(self, text):
        """Writes the given `text` on the remote machine without appending
        a newline.

        Unlike `Write`, this keyword returns and [#Interactive shells|consumes]
        nothing.

        Example:
        | Write Bare     | su\\n            |
        | ${output}=     | Read             |
        | Should Contain | ${output}        | su                         | # Was not consumed from output |
        | Should Contain | ${output}        | Password:                  |
        | Write Bare     | invalidpasswd\\n |
        | ${output}=     | Read             |
        | Should Contain | ${output}        | su: Authentication failure |

        See also `Write`.
        """
        self._write(text)

    def _write(self, text, add_newline=False):
        try:
            self.current.write(text, add_newline)
        except SSHClientException, e:
            raise RuntimeError(e)

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes given `text` repeatedly until `expected` appears in
        the server output.

        `text` is written without appending a newline and is
        [#Interactive shells|consumed] from the server output before
        `expected` is read.

        `retry_interval` defines the time before writing `text` again.

        The written `text` is logged with the defined `loglevel`.

        If `expected` does not appear in output within `timeout`, this keyword
        fails.

        Both `timeout` and `retry_interval` must be given in Robot Framework's
        time format (e.g. `5`, `1 minute`, `2 min 3 s`, `4.5`).

        See `interactive shells` for more information on writing.

        This example will write `lsof -c python26\\n` (list all files
        currently opened by python 2.6), until `myscript.py` appears in the
        output. The command is written every 0.5 seconds. The keyword fails if
        `myscript.py` does not appear in the server output in 5 seconds:
        | Write Until Expected Output | lsof -c python26\\n | expected=myscript.py | timeout=5s | retry_interval=0.5s |
        """
        self._read_and_log(loglevel, self.current.write_until_expected, text,
                           expected, timeout, retry_interval)

    def read(self, loglevel=None):
        """[#Interactive shells|Consumes] and returns everything available
        on the server output.

        This keyword is most useful for reading everything from
        the server output, thus clearing it.

        The read output is logged with the defined `loglevel`.

        See `interactive shells` for more information on reading.

        Example:
        | Open Connection | my.server.com |
        | Login           | johndoe       | secretpasswd                 |
        | Write           | sudo su -     |
        | ${output}=      | Read          |
        | Should Contain  | ${output}     | [sudo] password for johndoe: |
        | Write           | secretpasswd  |
        | ${output}=      | Read          | loglevel=WARN                | # Shown in the console due to loglevel |
        | Should Contain  | ${output}     | root@                        |
        """
        return self._read_and_log(loglevel, self.current.read)

    def read_until(self, expected, loglevel=None):
        """[#Interactive shells|Consumes] and returns the server output until
        `expected` is encountered.

        Text up until and including the `expected` will be returned.

        If [#Default timeout|the timeout] expires before the match is found,
        this keyword fails.

        The read output is logged with the defined `loglevel`.

        See `interactive shells` for more information on reading.

        Example:
        | Open Connection | my.server.com |
        | Login           | johndoe       | ${PASSWORD}                  |
        | Write           | sudo su -     |
        | ${output}=      | Read Until    | :                            |
        | Should Contain  | ${output}     | [sudo] password for johndoe: |
        | Write           | ${PASSWORD}   |
        | ${output}=      | Read Until    | @                            |
        | Should Contain  | ${output}     | root@                        |

        See also `Read Until Prompt` and `Read Until Regexp`.
        """
        return self._read_and_log(loglevel, self.current.read_until, expected)

    def read_until_prompt(self, loglevel=None):
        """[#Interactive shells|Consumes] and returns the server output until
        the prompt is found.

        Text up and until prompt is returned.
        [#Default prompt|Prompt must be set] before this keyword is used.

        If [#Default timeout|the timeout] expires before the match is found,
        this keyword fails.

        The read output is logged with the defined `loglevel`.

        See `interactive shells` for more information on reading.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and that command does not
        produce prompt characters in its output.

        Example:
        | Open Connection          | my.server.com     | prompt=$                    |
        | Login                    | johndoe           | ${PASSWORD}                 |
        | Write                    | sudo su -         |
        | Write                    | ${PASSWORD}       |
        | Set Client Configuration | prompt=#          | # For root, the prompt is # |
        | ${output}=               | Read Until Prompt |                             |
        | Should Contain           | ${output}         | root@myserver:~#            |

        See also `Read Until` and `Read Until Regexp`.
        """
        return self._read_and_log(loglevel, self.current.read_until_prompt)

    def read_until_regexp(self, regexp, loglevel=None):
        """[#Interactive shells|Consumes] and returns the server output until
        a match to `regexp` is found.

        `regexp` can be a pattern or a compiled regexp object.

        Text up until and including the `regexp` will be returned.

        Regular expression check is done using the Python 're' module, which
        has a pattern syntax derived from Perl, and thus also very similar to
        the one in Java. See the following documents for more details about
        regular expressions in general and Python implementation in particular.

        | http://docs.python.org/lib/module-re.html
        | http://www.amk.ca/python/howto/regex/

        Things to note about the `regexp` syntax:

        - Backslash is an escape character in the test data, and possible
          backslashes in the pattern must thus be escaped with another backslash
          (e.g. '\\\\d\\\\w+').

        - Possible flags altering how the expression is parsed (e.g.
          re.IGNORECASE, re.MULTILINE) can be set by prefixing the pattern with
          the '(?iLmsux)' group (e.g. '(?im)pattern'). The available flags are
          'IGNORECASE': 'i', 'MULTILINE': 'm', 'DOTALL': 's', 'VERBOSE': 'x',
          'UNICODE': 'u', and 'LOCALE': 'L'.

        If [#Default timeout|the timeout] expires before the match is found,
        this keyword fails.

        The read output is logged with the defined `loglevel`.

        See `interactive shells` for more information on reading.

        Example:
        | Open Connection | my.server.com     |
        | Login           | johndoe           | ${PASSWORD}                  |
        | Write           | sudo su -         |
        | ${output}=      | Read Until Regexp | \\\\[.*\\\\].*:              |
        | Should Contain  | ${output}         | [sudo] password for johndoe: |
        | Write           | ${PASSWORD}       |
        | ${output}=      | Read Until Regexp | .*@                          |
        | Should Contain  | ${output}         | root@                        |

        See also `Read Until` and `Read Until Prompt`.
        """
        return self._read_and_log(loglevel, self.current.read_until_regexp,
                                  regexp)

    def _read_and_log(self, loglevel, reader, *args):
        try:
            output = reader(*args)
        except SSHClientException, e:
            raise RuntimeError(e)
        self._log(output, loglevel)
        return output

    def get_file(self, source, destination='.', path_separator='/'):
        """Downloads file(s) from the remote machine to the local machine.

        `source` is a path on the remote machine. Relative or absolute
        path may be used.

        `destination` is the target path on the local machine. Relative or
        absolute path may be used.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-like operating systems,
        this is `/` which is also the default value. With Windows remotes,
        this must be set as `\\`. This option was added in SSHLibrary 1.1.

        1. If `destination` is an existing file, `source` file is downloaded
           over it.

        2. If `destination` is an existing directory, `source` file is
           downloaded into it. Possible file with the same name is overwritten.

        3. If `destination` does not exist and it ends with `path_separator`,
           it is considered a directory. The directory is then created and
           `source` file is downloaded into it. Possible missing intermediate
           directories are also created.

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
        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # Single file    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # All text files |
        """
        return self._run_sftp_command(self.current.get_file, source,
                                      destination, path_separator)

    def get_directory(self, source, destination='.', path_separator='/',
                      recursive=False):
        """Downloads a directory, including its content, from the remote
        machine to the local machine.

        `source` is a path on the remote machine. Relative or absolute
        path may be used.

        `destination` is the target path on the local machine. Relative or
        absolute path may be used.

        1. If `destination` is an existing path on the local machine,
           `source` directory is downloaded into it.

           In this example, remote `source`, `/var/logs`, is downloaded into
           an existing local `destination` `/home/robot`:
           | Get Directory | /var/logs | /home/robot |

           As a result, the content of remote directory `/var/logs` is now
           found at `/home/robot/logs`. Subdirectories are not included.

        2. If `destination` is a non-existing path on the local machine,
           the local path is created and the content of `source` directory is
           downloaded into it.

           In this example, the content of the remote `source`,
           directory `logs`, in downloaded to a non-existing local
           `destination` `my_new_path`:
           | Get Directory | logs | my_new_path |

           Note the use of relative paths in both `source` and `destination`.

           Because `my_new_path` does not already exist on the local machine,
           it is created. As the result of keyword, `my_new_path` now has the
           same content as the remote directory `logs` but not the `logs`
           directory itself. Subdirectories are not included.

        3. If `destination` is not given, `source` directory is downloaded into
           the current working directory on the local machine.
           This will most probably be the directory where the test execution
           was started.

           In this example, `source` is downloaded into the current working
           directory:
           | Get Directory | /path/to/remote/logs |

           Note the missing `destination`. It is also possible to refer
           to the current working directory by using `.`. This works both on
           the local and the remote side.

           In this case, `destination` always exists. As a result,
           the remote directory `logs` can be now found at the current
           working directory by name `logs`. Subdirectories are not included.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-like operating systems,
        this must be `/` which is also the default value. With Windows remotes,
        this must be set as `\\`.

        `recursive` specifies, whether to recursively download all
        subdirectories inside `source`. Subdirectories are downloaded if
        the argument value evaluates to `True`. The default value is `False`.

        The following example is identical to (1.), but also the subdirectories
        (and subdirectories of the subdirectories, ad infinitum) inside
        `source`, `/var/logs`, are downloaded:
        | Get Directory | /var/logs | /home/robot | recursive=True |

        As a result, the content of the remote directory `/var/logs`,
        including its subdirectories, is now found at `/home/robot/logs`.
        Subdirectory paths are preserved, e.g. remote `var/logs/mysql`
        is now found at `/home/robot/logs/mysql`.

        New in SSHLibrary 1.2.
        """
        return self._run_sftp_command(self.current.get_directory, source,
                                      destination, path_separator, recursive)

    def put_file(self, source, destination='.', mode='0744', newline="",
                 path_separator='/'):
        """Uploads file(s) from the local machine to the remote machine.

        `source` is the path on the local machine. Relative or absolute
        path may be used.

        `destination` is the target path on the remote machine. Relative or
        absolute path may be used.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-like operating systems,
        this is `/` which is also the default value. With Windows remotes,
        this must be set as `\\`. This option was added in SSHLibrary 1.1.

        `mode` argument can be used to set the target file permission.
        Numeric values are accepted. The default value is `0744` (-rwxr--r--).

        `newline` can be used to force newline characters that are written to
        the remote file. Valid values are `CRLF` (for Windows) and `LF`.

        1. If `destination` is an existing file, `source` file is uploaded
           over it.

        2. If `destination` is an existing directory, `source` file is
           uploaded into it. Possible file with same name is overwritten.

        3. If `destination` does not exist and it ends with `path_separator`,
           it is considered a directory. The directory is then created and
           `source` file uploaded into it. Possibly missing intermediate
           directories are also created.

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
        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt |        |      | # Single file                                     |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               |        |      | # All text files                                  |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               |  0777  | CRLF | # Custom permissions and forcing Windows newlines |
        """
        return self._run_sftp_command(self.current.put_file, source,
                                      destination, mode, newline,
                                      path_separator)

    def put_directory(self, source, destination='.', mode='0744',
                      newline="", path_separator='/', recursive=False):
        """Uploads a directory, including its content, from the local machine
        to the remote machine.

        `source` is the path on the local machine. Relative or absolute
        path may be used.

        `destination` is the target path on the remote machine. Relative or
        absolute path may be used.

        1. If `destination` is an existing path on the remote machine,
           `source` directory is uploaded into it.

           In this example, local `source`, `/var/logs`, is uploaded into
           an already existing remote `destination` `/home/robot`:
           | Put Directory | /var/logs | /home/robot |

           As a result, the content of local directory `/var/logs` is now
           found on the remote machine at `/home/robot/logs`.
           Subdirectories are not included.

        2. If `destination` is a non-existing path on the remote machine,
           it is created and the content of `source` directory is uploaded
           into it.

           In this example, the content of the local `source` directory `logs`,
           in the current working directory, is uploaded to a non-existing
           remote `destination` `my_new_path`:
           | Put Directory | logs | my_new_path |

           Note the use of relative paths in both `source` and `destination`.

           Because `my_new_path` does not already exist on the remote,
           it is created. As the result of keyword, `my_new_path` now has the
           same content as the local directory `logs` but not the `logs`
           directory itself. Subdirectories are not included.

        3. If `destination` is not given, `source` directory is uploaded into
           the current working directory on the remote machine.

           In this example, `source` is uploaded into the current working
           directory on the remote machine:
           | Put Directory | /path/to/remote/logs |

           Note the missing `destination`. It is also possible to refer
           to the current working directory by using `.`. This works both on
           the local and the remote side.

           In this case, `destination` always exists. As a result,
           the local directory `logs` is now found at the current remote
           working directory by name `logs`. Subdirectories are not included.

        `mode` argument can be used to set the file permissions.
        Numeric values are accepted. The default value is `0744` (-rwxr--r--).

        `newline` can be used to force newline characters that are written to
        the remote files. Valid values are `CRLF` (for Windows) and `LF`.

        `path_separator` is the path separator character of the operating system
        on the remote machine. On Unix-like operating systems,
        this must be `/` which is also the default value. With Windows remotes,
        this must be set as `\\`.

        `recursive` specifies, whether to recursively upload all
        subdirectories inside `source`. Subdirectories are uploaded if the
        argument value evaluates to `True`. The default value is `False`.

        The following example is identical to (1.), but also the subdirectories
        (and subdirectories of the subdirectories, ad infinitum) inside
        `source`, `/var/logs`, are uploaded:
        | Put Directory | /var/logs | /home/robot | recursive=True |

        As a result, the content of the local directory `/var/logs`,
        including its subdirectories, is now found on the remote at
        `/home/robot/logs`. Subdirectory paths are preserved, e.g.
        local `var/logs/mysql` is found on the remote machine
        at `/home/robot/logs/mysql`.

        New in SSHLibrary 1.2.
        """
        return self._run_sftp_command(self.current.put_directory, source,
                                      destination, mode, newline,
                                      path_separator, recursive)

    def _run_sftp_command(self, command, *args):
        try:
            sources, destinations = command(*args)
        except SSHClientException, e:
            raise RuntimeError(e)
        for src, dst in zip(sources, destinations):
            self._info("'%s' -> '%s'" % (src, dst))

    def file_should_exist(self, path):
        """Fails if the given `path` does NOT point to an existing file.

        Example:
        | File Should Exist | /boot/initrd.img |

        Note that symlinks are followed:
        | File Should Exist | /initrd.img | # Points to boot/initrd.img |

        New in SSHLibrary 1.2.
        """
        return self.current.file_exists(path)

    def file_should_not_exist(self, path):
        """Fails if the given `path` points to an existing file.

        Example:
        | File Should Not Exist | /cat |

        Note that this keyword follows symlinks. Thus the example would fail
        if `/cat` pointed to an existing file.

        New in SSHLibrary 1.2.
        """
        return not self.current.file_exists(path)

    def directory_should_exist(self, path):
        """Fails if the given `path` does not point to an existing directory.

        Example:
        | Directory Should Exist | /usr/share/man |

        Note that symlinks are followed:
        | Directory Should Exist | /usr/local/man | # Points to /usr/share/man/ |

        New in SSHLibrary 1.2.
        """
        return self.current.dir_exists(path)

    def directory_should_not_exist(self, path):
        """Fails if the given `path` points to an existing directory.

        Example:
        | Directory Should Not Exist | /nonexisting |

        Note that this keyword follows symlinks. Thus the example would fail
        if `/nonexisting` pointed to an existing directory.

        New in SSHLibrary 1.2.
        """
        return not self.current.dir_exists(path)

    def list_directory(self, path, pattern=None, absolute=False):
        """Returns and logs items in a remote directory, optionally filtered
        with `pattern`.

        File and directory names are returned in case-sensitive alphabetical
        order, e.g. ['A Name', 'Second', 'a lower case name', 'one more'].
        Implicit directories `.` and `..` are not returned. The returned items
        are automatically logged.

        By default, the file and directory names are returned relative to the
        given remote path (e.g. `file.txt`). If you want them be returned in the
        absolute format (e.g. `/home/robot/file.txt`), set the `absolute`
        argument to any non-empty string.

        If `pattern` is given, only items matching it are returned. The pattern
        matching syntax is explained in `pattern matching`.

        Examples (using also other `List Directory` variants):
        | @{items}= | List Directory          | /home/robot |
        | @{files}= | List Files In Directory | /tmp        | *.txt | absolute=True |

        If you are only interested in directories or files,
        use `List Files In Directory` or `List Directories In Directory`,
        respectively.

        New in SSHLibrary 1.2.
        """
        try:
            items = self.current.list_dir(path, pattern, absolute)
        except SSHClientException, msg:
            raise RuntimeError(msg)
        self._info('%d item%s:\n%s' % (len(items), plural_or_not(items),
                                       '\n'.join(items)))
        return items

    def list_files_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only files.

        New in SSHLibrary 1.2.
        """
        try:
            files = self.current.list_files_in_dir(path, pattern, absolute)
        except SSHClientException, msg:
            raise RuntimeError(msg)
        files = self.current.list_files_in_dir(path, pattern, absolute)
        self._info('%d file%s:\n%s' % (len(files), plural_or_not(files),
                                       '\n'.join(files)))
        return files

    def list_directories_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only directories.

        New in SSHLibrary 1.2.
        """
        try:
            dirs = self.current.list_dirs_in_dir(path, pattern, absolute)
        except SSHClientException, msg:
            raise RuntimeError(msg)
        self._info('%d director%s:\n%s' % (len(dirs),
                                          'y' if len(dirs) == 1 else 'ies',
                                          '\n'.join(dirs)))
        return dirs

    def _info(self, msg):
        self._log(msg, 'INFO')

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


class _DefaultConfiguration(Configuration):

    def __init__(self, timeout, newline, prompt, loglevel, term_type, width,
                 height, encoding):
        super(_DefaultConfiguration, self).__init__(
            timeout=TimeEntry(timeout),
            newline=NewlineEntry(newline),
            prompt=StringEntry(prompt),
            loglevel=LogLevelEntry(loglevel),
            term_type=StringEntry(term_type),
            width=IntegerEntry(width),
            height=IntegerEntry(height),
            encoding=StringEntry(encoding)
        )
