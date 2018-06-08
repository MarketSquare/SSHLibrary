#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from __future__ import print_function

try:
    from robot.api import logger
except ImportError:
    logger = None

from .abstractclient import SSHClientException
from .client import SSHClient
from .config import (Configuration, IntegerEntry, LogLevelEntry, NewlineEntry,
                     StringEntry, TimeEntry)
from .utils import ConnectionCache, is_string, is_truthy, plural_or_not
from .version import VERSION


__version__ = VERSION


class SSHLibrary(object):
    """SSHLibrary is a Robot Framework test library for SSH and SFTP.

     This document explains how to use keywords provided by SSHLibrary.
     For information about installation, support, and more please visit the
     [https://github.com/robotframework/SSHLibrary|project page].
     For more information about Robot Framework, see http://robotframework.org.

    The library has the following main usages:
    - Executing commands on the remote machine, either with blocking or
      non-blocking behaviour (see `Execute Command` and `Start Command`,
      respectively).
    - Writing and reading in an interactive shell (e.g. `Read` and `Write`).
    - Transferring files and directories over SFTP (e.g. `Get File` and
      `Put Directory`).
    - Ensuring that files or directories exist on the remote machine
      (e.g. `File Should Exist` and `Directory Should Not Exist`).

    This library works both with Python and Jython, but uses different
    SSH modules internally depending on the interpreter. See
    [http://robotframework.org/SSHLibrary/#installation|installation instructions]
    for more details about the dependencies. IronPython is unfortunately
    not supported. Python 3 is supported starting from SSHLibrary 3.0.0.

    == Table of contents ==

    - `Connections and login`
    - `Configuration`
    - `Executing commands`
    - `Interactive shells`
    - `Pattern matching`
    - `Example`
    - `Importing`
    - `Boolean arguments`
    - `Shortcuts`
    - `Keywords`

    = Connections and login =

    SSHLibrary supports multiple connections to different hosts.
    New connections are opened with `Open Connection`.

    Login into the host is done either with username and password
    (`Login`) or with public/private key pair (`Login With Public key`).

    Only one connection can be active at a time. This means that most of the
    keywords only affect the active connection. Active connection can be
    changed with `Switch Connection`.

    = Configuration =

    Default settings for all the upcoming connections can be configured on
    `library importing` or later with `Set Default Configuration`.

    Using `Set Default Configuration` does not affect the already open
    connections. Settings of the current connection can be configured
    with `Set Client Configuration`. Settings of another, non-active connection,
    can be configured by first using `Switch Connection` and then
    `Set Client Configuration`.

    Most of the defaults can be overridden per connection by defining them
    as arguments to `Open Connection`. Otherwise the defaults are used.

    == Configurable per connection ==

    === Prompt ===

    Argument ``prompt`` defines the character sequence used by `Read Until Prompt`
    and must be set before that keyword can be used.

    If you know the prompt on the remote machine, it is recommended to set it
    to ease reading output from the server after using `Write`. In addition to
    that, `Login` and `Login With Public Key` can read the server output more
    efficiently when the prompt is set.

    Prompt can be specified either as a normal string or as a regular expression.
    The latter is especially useful if the prompt changes as a result of
    the executed commands. Prompt can be set to be a regular expression by
    giving the prompt argument a value starting with ``REGEXP:`` followed by
    the actual regular expression like ``prompt=REGEXP:[$#]``. See the
    `Regular expressions` section for more details about the syntax.

    The support for regular expressions is new in SSHLibrary 3.0.0.

    === Encoding ===

    Argument ``encoding`` defines the
    [https://docs.python.org/3/library/codecs.html#standard-encodings|
    character encoding] of input and output sequences. The default encoding
    is UTF-8.

    === Path separator ===

    Argument ``path_separator`` must be set to the one known by the operating
    system and the SSH server on the remote machine. The path separator is
    used by keywords `Get File`, `Put File`, `Get Directory` and
    `Put Directory` for joining paths correctly on the remote host.

    The default path separator is forward slash ``/`` which works on
    Unix-like machines. On Windows the path separator to use depends on
    the SSH server. Some servers use forward slash and others backslash,
    and users need to configure the ``path_separator`` accordingly. Notice
    that using a backslash in Robot Framework test data requires doubling
    it like ``\\\\``.

    The path separator can be configured on `library importing` or later,
    using `Set Default Configuration`, `Set Client Configuration` and `Open
    Connection`.

    === Timeout ===

    Argument ``timeout`` is used by `Read Until` variants. The default value
    is ``3 seconds``.

    Value must be in Robot Framework's time format such as ``3``, ``4.5s``,
    ``1 minute`` and ``2 min 3 s``.  For more information about the time
    syntax see the
    [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|
    Robot Framework User Guide].

    === Newline ===

    Argument ``newline`` is the line break sequence used by `Write` keyword
    and must be set according to the operating system on the remote machine.
    The default value is ``LF`` (same as ``\\n``) which is used on Unix-like
    operating systems. With Windows remote machines, you need to set this to
    ``CRLF`` (``\\r\\n``).

    === Terminal settings ===

    Argument ``term_type`` defines the virtual terminal type, and arguments
    ``width`` and ``height`` can be used to control its  virtual size.

    == Not configurable per connection ==

    === Loglevel ===

    Argument ``loglevel`` sets the log level used to log the output read by
    `Read`, `Read Until`, `Read Until Prompt`, `Read Until Regexp`, `Write`,
    `Write Until Expected Output`, `Login` and `Login With Public Key`.
    The default level is ``INFO``.

    ``loglevel`` is not configurable per connection but can be overridden by
    passing it as an argument to the most of the aforementioned keywords.
    Possible argument values are ``TRACE``, ``DEBUG``, ``INFO`` and ``WARN``.

    = Executing commands =

    For executing commands on the remote machine, there are two possibilities:

    - `Execute Command` and `Start Command`.
       The command is executed in a new shell on the remote machine,
       which means that possible changes to the environment
       (e.g. changing working directory, setting environment variables, etc.)
       are not visible to the subsequent keywords.

    - `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
      `Read Until`, `Read Until Prompt` and `Read Until Regexp`.
       These keywords operate in an interactive shell, which means that changes
       to the environment are visible to the subsequent keywords.

    = Interactive shells =

    `Write`, `Write Bare`, `Write Until Expected Output`, `Read`,
    `Read Until`, `Read Until Prompt` and `Read Until Regexp` can be used
    to interact with the server within the same shell.

    == Consumed output ==

    All of these keywords, except `Write Bare`, consume the read or the written
    text from the server output before returning. In practice this means that
    the text is removed from the server output, i.e. subsequent calls to
    `Read` keywords do not return text that was already read. This is
    illustrated by the example below.

    | `Write`              | echo hello   |       | # Consumes written ``echo hello``                  |
    | ${stdout}=           | `Read Until` | hello | # Consumes read ``hello`` and everything before it |
    | `Should Contain`     | ${stdout}    | hello |
    | ${stdout}=           | `Read`       |       | # Consumes everything available                    |
    | `Should Not Contain` | ${stdout}    | hello | # ``hello`` was already consumed earlier           |

    The consumed text is logged by the keywords and their argument
    ``loglevel`` can be used to override the default `log level`.

    `Login` and `Login With Public Key` consume everything on the server
    output or if the `prompt` is set, everything until the prompt.

    == Reading ==

    `Read`, `Read Until`, `Read Until Prompt` and `Read Until Regexp` can be
    used to read from the server. The read text is also consumed from
    the server output.

    `Read` reads everything available on the server output, thus clearing it.

    `Read Until` variants read output up until and *including* ``expected``
    text. These keywords will fail if the `timeout` expires before
    ``expected`` is found.

    == Writing ==

    `Write` and `Write Until Expected Output` consume the written text
    from the server output while `Write Bare` does not.

    These keywords do not return any output triggered by the written text.
    To get the output, one of the `Read` keywords must be explicitly used.

    = Pattern matching =

    == Glob patterns ==

    Some keywords allow their arguments to be specified as _glob patterns_
    where:
    | *        | matches anything, even an empty string |
    | ?        | matches any single character |
    | [chars]  | matches any character inside square brackets (e.g. ``[abc]`` matches either ``a``, ``b`` or ``c``) |
    | [!chars] | matches any character not inside square brackets |

    Pattern matching is case-sensitive regardless the local or remote
    operating system. Matching is implemented using Python's
    [https://docs.python.org/3/library/fnmatch.html|fnmatch module].

    == Regular expressions ==

    Some keywords support pattern matching using regular expressions, which
    are more powerful but also more complicated than `glob patterns`. This
    library uses Python's regular expressions, which are introduced in the
    [https://docs.python.org/3/howto/regex.html|Regular Expression HOWTO].

    Remember that in Robot Framework data the backslash that is used a lot
    in regular expressions is an escape character and needs to be doubled
    to get a literal backslash. For example, ``\\\\d\\\\d\\\\s`` matches
    two digits followed by a whitespace character.

    Possible flags altering how the expression is parsed (e.g.
    ``re.IGNORECASE``, ``re.MULTILINE``) can be set by prefixing the pattern
    with the ``(?iLmsux)`` group. The available flags are ``IGNORECASE``:
    ``i``, ``MULTILINE``: ``m``, ``DOTALL``: ``s``, ``VERBOSE``: ``x``,
    ``UNICODE``: ``u``, and ``LOCALE``: ``L``. For example, ``(?is)pat.ern``
    uses ``IGNORECASE`` and ``DOTALL`` flags.

    = Example =

    | ***** Settings *****
    | Documentation          This example demonstrates executing commands on a remote machine
    | ...                    and getting their output and the return code.
    | ...
    | ...                    Notice how connections are handled as part of the suite setup and
    | ...                    teardown. This saves some time when executing several test cases.
    |
    | Library                `SSHLibrary`
    | Suite Setup            `Open Connection And Log In`
    | Suite Teardown         `Close All Connections`
    |
    | ***** Variables *****
    | ${HOST}                localhost
    | ${USERNAME}            test
    | ${PASSWORD}            test
    |
    | ***** Test Cases *****
    | Execute Command And Verify Output
    |     [Documentation]    Execute Command can be used to ran commands on the remote machine.
    |     ...                The keyword returns the standard output by default.
    |     ${output}=         `Execute Command`  echo Hello SSHLibrary!
    |     `Should Be Equal`    ${output}        Hello SSHLibrary!
    |
    | Execute Command And Verify Return Code
    |     [Documentation]    Often getting the return code of the command is enough.
    |     ...                This behaviour can be adjusted as Execute Command arguments.
    |     ${rc}=             `Execute Command`  echo Success guaranteed.    return_stdout=False    return_rc=True
    |     `Should Be Equal`    ${rc}            ${0}
    |
    | Executing Commands In An Interactive Session
    |     [Documentation]    Execute Command always executes the command in a new shell.
    |     ...                This means that changes to the environment are not persisted
    |     ...                between subsequent Execute Command keyword calls.
    |     ...                Write and Read Until variants can be used to operate in the same shell.
    |     `Write`              cd ..
    |     `Write`              echo Hello from the parent directory!
    |     ${output}=         `Read Until`       directory!
    |     `Should End With`    ${output}        Hello from the parent directory!
    |
    | ***** Keywords *****
    | Open Connection And Log In
    |    `Open Connection`     ${HOST}
    |    `Login`               ${USERNAME}        ${PASSWORD}

    Save the content as file ``executing_command.txt`` and run:

    ``robot executing_commands.txt``

    You may want to override the variables from commandline to try this out on
    your remote machine:

    ``robot -v HOST:my.server.com -v USERNAME:johndoe -v PASSWORD:secretpasswd executing_commands.txt``

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is either an empty string or case-insensitively equal to ``false``,
    ``none`` or ``no``. Other strings are considered true regardless
    their value, and other argument types are tested using the same
    [http://docs.python.org/2/library/stdtypes.html#truth-value-testing|rules
    as in Python].

    True examples:
    | `List Directory` | ${path} | recursive=True    | # Strings are generally true.    |
    | `List Directory` | ${path} | recursive=yes     | # Same as the above.             |
    | `List Directory` | ${path} | recursive=${TRUE} | # Python ``True`` is true.       |
    | `List Directory` | ${path} | recursive=${42}   | # Numbers other than 0 are true. |
    False examples:
    | `List Directory` | ${path} | recursive=False    | # String ``false`` is false.   |
    | `List Directory` | ${path} | recursive=no       | # Also string ``no`` is false. |
    | `List Directory` | ${path} | recursive=${EMPTY} | # Empty string is false.       |
    | `List Directory` | ${path} | recursive=${FALSE} | # Python ``False`` is false.   |

    Prior to SSHLibrary 3.1, all non-empty strings, including ``no`` and ``none``
    were considered to be true. Considering ``none`` false is new in Robot Framework 3.0.3.
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
    DEFAULT_PATH_SEPARATOR = '/'
    DEFAULT_ENCODING = 'UTF-8'

    def __init__(self,
                 timeout=DEFAULT_TIMEOUT,
                 newline=DEFAULT_NEWLINE,
                 prompt=DEFAULT_PROMPT,
                 loglevel=DEFAULT_LOGLEVEL,
                 term_type=DEFAULT_TERM_TYPE,
                 width=DEFAULT_TERM_WIDTH,
                 height=DEFAULT_TERM_HEIGHT,
                 path_separator=DEFAULT_PATH_SEPARATOR,
                 encoding=DEFAULT_ENCODING):
        """SSHLibrary allows some import time `configuration`.

        If the library is imported without any arguments, the library
        defaults are used:

        | Library | SSHLibrary |

        Only arguments that are given are changed. In this example the
        `timeout` is changed to ``10 seconds`` but  other settings are left
        to the library defaults:

        | Library | SSHLibrary | 10 seconds |

        The `prompt` does not have a default value and
        must be explicitly set to be able to use `Read Until Prompt`.
        Since SSHLibrary 3.0.0, the prompt can also be a regular expression:

        | Library | SSHLibrary | prompt=REGEXP:[$#] |

        Multiple settings are also possible. In the example below, the library
        is brought into use with `newline` and `path separator` known by
        Windows:

        | Library | SSHLibrary | newline=CRLF | path_separator=\\\\ |
        """
        self._connections = ConnectionCache()
        self._config = _DefaultConfiguration(
            timeout or self.DEFAULT_TIMEOUT,
            newline or self.DEFAULT_NEWLINE,
            prompt or self.DEFAULT_PROMPT,
            loglevel or self.DEFAULT_LOGLEVEL,
            term_type or self.DEFAULT_TERM_TYPE,
            width or self.DEFAULT_TERM_WIDTH,
            height or self.DEFAULT_TERM_HEIGHT,
            path_separator or self.DEFAULT_PATH_SEPARATOR,
            encoding or self.DEFAULT_ENCODING
        )

    @property
    def current(self):
        return self._connections.current

    def set_default_configuration(self, timeout=None, newline=None, prompt=None,
                                  loglevel=None, term_type=None, width=None,
                                  height=None, path_separator=None,
                                  encoding=None):
        """Update the default `configuration`.

        Please note that using this keyword does not affect the already
        opened connections. Use `Set Client Configuration` to configure the
        active connection.

        Only parameters whose value is other than ``None`` are updated.

        This example sets `prompt` to ``$``:

        | `Set Default Configuration` | prompt=$ |

        This example sets `newline` and `path separator` to the ones known
        by Windows:

        | `Set Default Configuration` | newline=CRLF | path_separator=\\\\ |

        Sometimes you might want to use longer `timeout` for all the
        subsequent connections without affecting the existing ones:

        | `Set Default Configuration`   | timeout=5 seconds  |
        | `Open Connection       `      | local.server.com   |
        | `Set Default Configuration`   | timeout=20 seconds |
        | `Open Connection`             | emea.server.com    |
        | `Open Connection`             | apac.server.com    |
        | ${local}                      | ${emea}            | ${apac}= | `Get Connections` |
        | `Should Be Equal As Integers` | ${local.timeout}   | 5        |
        | `Should Be Equal As Integers` | ${emea.timeout}    | 20       |
        | `Should Be Equal As Integers` | ${apac.timeout}    | 20       |
        """
        self._config.update(timeout=timeout, newline=newline, prompt=prompt,
                            loglevel=loglevel, term_type=term_type, width=width,
                            height=height, path_separator=path_separator,
                            encoding=encoding)

    def set_client_configuration(self, timeout=None, newline=None, prompt=None,
                                 term_type=None, width=None, height=None,
                                 path_separator=None, encoding=None):
        """Update the `configuration` of the current connection.

        Only parameters whose value is other than ``None`` are updated.

        In the following example, `prompt` is set for
        the current connection. Other settings are left intact:

        | `Open Connection    `      | my.server.com      |
        | `Set Client Configuration` | prompt=$           |
        | ${myserver}=               | `Get Connection`   |
        | `Should Be Equal`          | ${myserver.prompt} | $ |

        Using keyword does not affect the other connections:

        | `Open Connection`          | linux.server.com   |                   |
        | `Set Client Configuration` | prompt=$           |                   | # Only linux.server.com affected   |
        | `Open Connection    `      | windows.server.com |                   |
        | `Set Client Configuration` | prompt=>           |                   | # Only windows.server.com affected |
        | ${linux}                   | ${windows}=        | `Get Connections` |
        | `Should Be Equal`          | ${linux.prompt}    | $                 |
        | `Should Be Equal`          | ${windows.prompt}  | >                 |

        Multiple settings are possible. This example updates the
        `terminal settings` of the current connection:

        | `Open Connection`          | 192.168.1.1    |
        | `Set Client Configuration` | term_type=ansi | width=40 |
        """
        self.current.config.update(timeout=timeout, newline=newline,
                                   prompt=prompt, term_type=term_type,
                                   width=width, height=height,
                                   path_separator=path_separator,
                                   encoding=encoding)

    def enable_ssh_logging(self, logfile):
        """Enables logging of SSH protocol output to given ``logfile``.

        All the existing and upcoming connections are logged onwards from
        the moment the keyword was called.

        ``logfile`` is path to a file that is writable by the current local
        user. If the file already exists, it will be overwritten.

        Example:
        | `Open Connection`    | my.server.com   | # Not logged |
        | `Enable SSH Logging` | myserver.log    |
        | `Login`              | johndoe         | secretpasswd |
        | `Open Connection`    | build.local.net | # Logged     |
        | # Do something with the connections    |
        | # Check myserver.log for detailed debug information   |

        *Note:* This keyword does not work when using Jython.
        """
        if SSHClient.enable_logging(logfile):
            self._log('SSH log is written to <a href="%s">file</a>.' % logfile,
                      'HTML')

    def open_connection(self, host, alias=None, port=22, timeout=None,
                        newline=None, prompt=None, term_type=None, width=None,
                        height=None, path_separator=None, encoding=None):
        """Opens a new SSH connection to the given ``host`` and ``port``.

        The new connection is made active. Possible existing connections
        are left open in the background.

        Note that on Jython this keyword actually opens a connection and
        will fail immediately on unreachable hosts. On Python the actual
        connection attempt will not be done until `Login` is called.

        This keyword returns the index of the new connection which can be used
        later to switch back to it. Indices start from ``1`` and are reset
        when `Close All Connections` is used.

        Optional ``alias`` can be given for the connection and can be used for
        switching between connections, similarly as the index.
        See `Switch Connection` for more details.

        Connection parameters, like `timeout` and `newline` are documented in
        `configuration`. If they are not defined as arguments, the library
        defaults are used for the connection.

        All the arguments, except ``host``, ``alias`` and ``port``
        can be later updated with `Set Client Configuration`.

        Port ``22`` is assumed by default:

        | ${index}= | `Open Connection` | my.server.com |

        Non-standard port may be given as an argument:

        | ${index}= | `Open Connection` | 192.168.1.1 | port=23 |

        Aliases are handy, if you need to switch back to the connection later:

        | `Open Connection`   | my.server.com | alias=myserver |
        | # Do something with my.server.com   |
        | `Open Connection`   | 192.168.1.1   |
        | `Switch Connection` | myserver      |                | # Back to my.server.com |

        Settings can be overridden per connection, otherwise the ones set on
        `library importing` or with `Set Default Configuration` are used:

        | Open Connection | 192.168.1.1     | timeout=1 hour    | newline=CRLF          |
        | # Do something with the connection                    |
        | `Open Connection` | my.server.com | # Default timeout | # Default line breaks |

        The `terminal settings` are also configurable per connection:

        | `Open Connection` | 192.168.1.1  | term_type=ansi | width=40 |
        """
        timeout = timeout or self._config.timeout
        newline = newline or self._config.newline
        prompt = prompt or self._config.prompt
        term_type = term_type or self._config.term_type
        width = width or self._config.width
        height = height or self._config.height
        path_separator = path_separator or self._config.path_separator
        encoding = encoding or self._config.encoding
        client = SSHClient(host, alias, port, timeout, newline, prompt,
                           term_type, width, height, path_separator, encoding)
        connection_index = self._connections.register(client, alias)
        client.config.update(index=connection_index)
        return connection_index

    def switch_connection(self, index_or_alias):
        """Switches the active connection by index or alias.

        ``index_or_alias`` is either connection index (an integer) or alias
        (a string). Index is got as the return value of `Open Connection`.
        Alternatively, both index and alias can queried as attributes
        of the object returned by `Get Connection`.

        This keyword returns the index of the previous active connection,
        which can be used to switch back to that connection later.

        Example:
        | ${myserver}=        | `Open Connection` | my.server.com |
        | `Login`             | johndoe           | secretpasswd  |
        | `Open Connection`   | build.local.net   | alias=Build   |
        | `Login`             | jenkins           | jenkins       |
        | `Switch Connection` | ${myserver}       |               | # Switch using index          |
        | ${username}=        | `Execute Command` | whoami        | # Executed on my.server.com   |
        | `Should Be Equal`   | ${username}       | johndoe       |
        | `Switch Connection` | Build             |               | # Switch using alias          |
        | ${username}=        | `Execute Command` | whoami        | # Executed on build.local.net |
        | `Should Be Equal`   | ${username}       | jenkins       |
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
        | `Open Connection`  | my.server.com  |
        | `Login`            | johndoe        | secretpasswd |
        | `Get File`         | results.txt    | /tmp         |
        | `Close Connection` |
        | # Do something with /tmp/results.txt               |
        """
        self.current.close()
        self._connections.current = self._connections._no_current

    def close_all_connections(self):
        """Closes all open connections.

        This keyword is ought to be used either in test or suite teardown to
        make sure all the connections are closed before the test execution
        finishes.

        After this keyword, the connection indices returned by
        `Open Connection` are reset and start from ``1``.

        Example:
        | `Open Connection` | my.server.com           |
        | `Open Connection` | build.local.net         |
        | # Do something with the connections         |
        | [Teardown]        | `Close all connections` |
        """
        self._connections.close_all()

    def get_connection(self, index_or_alias=None, index=False, host=False,
                       alias=False, port=False, timeout=False, newline=False,
                       prompt=False, term_type=False, width=False, height=False,
                       encoding=False):
        """Returns information about the connection.

        Connection is not changed by this keyword, use `Switch Connection` to
        change the active connection.

        If ``index_or_alias`` is not given, the information of the current
        connection is returned.

        This keyword returns an object that has the following attributes:

        | = Name =       | = Type = | = Explanation = |
        | index          | integer  | Number of the connection. Numbering starts from ``1``. |
        | host           | string   | Destination hostname. |
        | alias          | string   | An optional alias given when creating the connection.  |
        | port           | integer  | Destination port. |
        | timeout        | string   | `Timeout` length in textual representation. |
        | newline        | string   | The line break sequence used by `Write` keyword. See `newline`. |
        | prompt         | string   | `Prompt` character sequence for `Read Until Prompt`. |
        | term_type      | string   | Type of the virtual terminal. See `terminal settings`. |
        | width          | integer  | Width of the virtual terminal. See `terminal settings`. |
        | height         | integer  | Height of the virtual terminal. See `terminal settings`. |
        | path_separator | string   | The `path separator` used on the remote host. |
        | encoding       | string   | The `encoding` used for inputs and outputs. |

        If there is no connection, an object having ``index`` and ``host``
        as ``None`` is returned, rest of its attributes having their values
        as configuration defaults.

        If you want the information for all the open connections, use
        `Get Connections`.

        Getting connection information of the current connection:

        | `Open Connection` | far.server.com        |
        | `Open Connection` | near.server.com       | prompt=>>       | # Current connection |
        | ${nearhost}=      | `Get Connection`      |                 |
        | `Should Be Equal` | ${nearhost.host}      | near.server.com |
        | `Should Be Equal` | ${nearhost.index}     | 2               |
        | `Should Be Equal` | ${nearhost.prompt}    | >>              |
        | `Should Be Equal` | ${nearhost.term_type} | vt100           | # From defaults      |

        Getting connection information using an index:

        | `Open Connection` | far.server.com   |
        | `Open Connection` | near.server.com  | # Current connection |
        | ${farhost}=       | `Get Connection` | 1                    |
        | `Should Be Equal` | ${farhost.host}  | far.server.com       |

        Getting connection information using an alias:

        | `Open Connection` | far.server.com   | alias=far            |
        | `Open Connection` | near.server.com  | # Current connection |
        | ${farhost}=       | `Get Connection` | far                  |
        | `Should Be Equal` | ${farhost.host}  | far.server.com       |
        | `Should Be Equal` | ${farhost.alias} | far                  |

        This keyword can also return plain connection attributes instead of
        the whole connection object. This can be adjusted using the boolean
        arguments ``index``, ``host``, ``alias``, and so on, that correspond
        to the attribute names of the object. If such arguments are given, and
        they evaluate to true (see `Boolean arguments`), only the respective
        connection attributes are returned. Note that attributes are always
        returned in the same order arguments are specified in the signature.

        | `Open Connection` | my.server.com    | alias=example    |
        | ${host}=          | `Get Connection` | host=True        |
        | `Should Be Equal` | ${host}          | my.server.com    |
        | ${host}           | ${alias}=        | `Get Connection` | host=yes | alias=please |
        | `Should Be Equal` | ${host}          | my.server.com    |
        | `Should Be Equal` | ${alias}         | example          |

        Getting only certain attributes is especially useful when using this
        library via the Remote library interface. This interface does not
        support returning custom objects, but individual attributes can be
        returned just fine.

        This keyword logs the connection information with log level ``INFO``.
        """
        if not index_or_alias:
            index_or_alias = self._connections.current_index
        try:
            config = self._connections.get_connection(index_or_alias).config
        except RuntimeError:
            config = SSHClient(None).config
        self._info(str(config))
        return_values = tuple(self._get_config_values(config, index, host,
                                                      alias, port, timeout,
                                                      newline, prompt,
                                                      term_type, width, height,
                                                      encoding))
        if not return_values:
            return config
        if len(return_values) == 1:
            return return_values[0]
        return return_values

    def _info(self, msg):
        self._log(msg, 'INFO')

    def _log(self, msg, level=None):
        level = self._active_loglevel(level)
        msg = msg.strip()
        if not msg:
            return
        if logger:
            logger.write(msg, level)
        else:
            print('*%s* %s' % (level, msg))

    def _active_loglevel(self, level):
        if level is None:
            return self._config.loglevel
        if is_string(level) and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN', 'HTML']:
            return level.upper()
        raise AssertionError("Invalid log level '%s'." % level)

    def _get_config_values(self, config, index, host, alias, port, timeout,
                           newline, prompt, term_type, width, height, encoding):
        if is_truthy(index):
            yield config.index
        if is_truthy(host):
            yield config.host
        if is_truthy(alias):
            yield config.alias
        if is_truthy(port):
            yield config.port
        if is_truthy(timeout):
            yield config.timeout
        if is_truthy(newline):
            yield config.newline
        if is_truthy(prompt):
            yield config.prompt
        if is_truthy(term_type):
            yield config.term_type
        if is_truthy(width):
            yield config.width
        if is_truthy(height):
            yield config.height
        if is_truthy(encoding):
            yield config.encoding

    def get_connections(self):
        """Returns information about all the open connections.

        This keyword returns a list of objects that are identical to the ones
        returned by `Get Connection`.

        Example:
        | `Open Connection`             | near.server.com     | timeout=10s       |
        | `Open Connection`             | far.server.com      | timeout=5s        |
        | ${nearhost}                   | ${farhost}=         | `Get Connections` |
        | `Should Be Equal`             | ${nearhost.host}    | near.server.com   |
        | `Should Be Equal As Integers` | ${nearhost.timeout} | 10                |
        | `Should Be Equal As Integers` | ${farhost.port}     | 22                |
        | `Should Be Equal As Integers` | ${farhost.timeout}  | 5                 |

        This keyword logs the information of connections with log level
        ``INFO``.
        """
        configs = [c.config for c in self._connections._connections]
        for c in configs:
            self._info(str(c))
        return configs

    def login(self, username, password, delay='0.5 seconds'):
        """Logs into the SSH server with the given ``username`` and ``password``.

        Connection must be opened before using this keyword.

        This keyword reads, returns and logs the server output after logging
        in. If the `prompt` is set, everything until the prompt is read.
        Otherwise the output is read using the `Read` keyword with the given
        ``delay``. The output is logged using the default `log level`.

        Example that logs in and returns the output:

        | `Open Connection` | linux.server.com |
        | ${output}=        | `Login`          | johndoe       | secretpasswd |
        | `Should Contain`  | ${output}        | Last login at |

        Example that logs in and returns everything until the prompt:

        | `Open Connection` | linux.server.com | prompt=$         |
        | ${output}=        | `Login`          | johndoe          | secretpasswd |
        | `Should Contain`  | ${output}        | johndoe@linux:~$ |
        """
        return self._login(self.current.login, username, password, delay)

    def login_with_public_key(self, username, keyfile, password='',
                              allow_agent=False, look_for_keys=False,
                              delay='0.5 seconds'):
        """Logs into the SSH server using key-based authentication.

        Connection must be opened before using this keyword.

        ``username`` is the username on the remote machine.

        ``keyfile`` is a path to a valid OpenSSH private key file on the local
        filesystem.

        ``password`` is used to unlock the ``keyfile`` if needed.

        This keyword reads, returns and logs the server output after logging
        in. If the `prompt` is set, everything until the prompt is read.
        Otherwise the output is read using the `Read` keyword with the given
        ``delay``. The output is logged using the default `log level`.

        Example that logs in using a private key and returns the output:

        | `Open Connection` | linux.server.com        |
        | ${output}=        | `Login With Public Key` | johndoe       | /home/johndoe/.ssh/id_rsa |
        | `Should Contain`  | ${motd}                 | Last login at |

        With locked private keys, the keyring ``password`` is required:

        | `Open Connection`       | linux.server.com |
        | `Login With Public Key` | johndoe          | /home/johndoe/.ssh/id_dsa | keyringpasswd |

        ``allow_agent`` enables the connection to the SSH agent.
        ``look_for_keys`` enables the searching for discoverable private key
        files in ``~/.ssh/``.

        ``allow_agent`` and ``look_for_keys`` arguments are new in SSHLibrary
        3.0.0.

        *Note:* ``allow_agent`` and ``look_for_keys`` do not work when using Jython.
        """
        return self._login(self.current.login_with_public_key, username,
                           keyfile, password, is_truthy(allow_agent),
                           is_truthy(look_for_keys), delay)

    def _login(self, login_method, username, *args):
        self._info("Logging into '%s:%s' as '%s'."
                   % (self.current.config.host, self.current.config.port,
                      username))
        try:
            login_output = login_method(username, *args)
            self._log('Read output: %s' % login_output)
            return login_output
        except SSHClientException as e:
            raise RuntimeError(e)

    def get_pre_login_banner(self, host=None, port=22):
        """Returns the banner supplied by the server upon connect.

        There are 2 ways of getting banner information.

        1. Independent of any connection:

        | ${banner} =       | `Get Pre Login Banner` | ${HOST}                   |
        | `Should Be Equal` | ${banner}              | Testing pre-login banner  |

        The argument ``host`` is mandatory for getting banner key without
        an open connection.

        2. From the current connection:

        | `Open Connection`  | ${HOST}                | prompt=${PROMPT}         |
        | `Login`            | ${USERNAME}            | ${PASSWORD}              |
        | ${banner} =        | `Get Pre Login Banner` |
        | `Should Be Equal`  | ${banner}              | Testing pre-login banner |

        New in SSHLibrary 3.0.0.

        *Note:* This keyword does not work when using Jython.
        """
        if host:
            banner = SSHClient.get_banner_without_login(host, port)
        elif self.current:
            banner = self.current.get_banner()
        else:
            raise RuntimeError("'host' argument is mandatory if there is no open connection.")
        return banner.decode(self.DEFAULT_ENCODING)

    def execute_command(self, command, return_stdout=True, return_stderr=False,
                        return_rc=False, sudo=False,  sudo_password=None):
        """Executes ``command`` on the remote machine and returns its outputs.

        This keyword executes the ``command`` and returns after the execution
        has been finished. Use `Start Command` if the command should be
        started in the background.

        By default, only the standard output is returned:

        | ${stdout}=       | `Execute Command` | echo 'Hello John!' |
        | `Should Contain` | ${stdout}         | Hello John!        |

        Arguments ``return_stdout``, ``return_stderr`` and ``return_rc`` are
        used to specify, what is returned by this keyword.
        If several arguments evaluate to a true value (see `Boolean arguments`),
        multiple values are returned.

        If errors are needed as well, set the respective argument value to
        true:

        | ${stdout}         | ${stderr}= | `Execute Command` | echo 'Hello John!' | return_stderr=True |
        | `Should Be Empty` | ${stderr}  |

        Often checking the return code is enough:

        | ${rc}=                        | `Execute Command` | echo 'Hello John!' | return_stdout=False | return_rc=True |
        | `Should Be Equal As Integers` | ${rc}             | 0                  | # succeeded         |

        Arguments ``sudo`` and ``sudo_password`` are used for executing
        commands within a sudo session. Due to different permission elevation
        in Cygwin, these two arguments will not work when using it.

        | `Execute Command`  | pwd | sudo=True |  sudo_password=test |

        The ``command`` is always executed in a new shell. Thus possible
        changes to the environment (e.g. changing working directory) are not
        visible to the later keywords:

        | ${pwd}=           | `Execute Command` | pwd           |
        | `Should Be Equal` | ${pwd}            | /home/johndoe |
        | `Execute Command` | cd /tmp           |
        | ${pwd}=           | `Execute Command` | pwd           |
        | `Should Be Equal` | ${pwd}            | /home/johndoe |

        `Write` and `Read` can be used for running multiple commands in the
        same shell. See `interactive shells` section for more information.

        This keyword logs the executed command and its exit status with
        log level ``INFO``.

        ``sudo`` and ``sudo_password`` arguments are new in SSHLibrary 3.0.0.
        """
        sudo = is_truthy(sudo)
        if not sudo:
            self._info("Executing command '%s'." % command)
        else:
            self._info("Executing command 'sudo %s'." % command)
        opts = self._legacy_output_options(return_stdout, return_stderr,
                                           return_rc)
        stdout, stderr, rc = self.current.execute_command(command, sudo, sudo_password)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def start_command(self, command, sudo=False,  sudo_password=None):
        """Starts execution of the ``command`` on the remote machine and returns immediately.

        This keyword returns nothing and does not wait for the ``command``
        execution to be finished. If waiting for the output is required,
        use `Execute Command` instead.

        This keyword does not return any output generated by the started
        ``command``. Use `Read Command Output` to read the output:

        | `Start Command`   | echo 'Hello John!'    |
        | ${stdout}=        | `Read Command Output` |
        | `Should Contain`  | ${stdout}             | Hello John! |

        The ``command`` is always executed in a new shell, similarly as with
        `Execute Command`. Thus possible changes to the environment (e.g.
        changing working directory) are not visible to the later keywords:

        | `Start Command`   | pwd                   |
        | ${pwd}=           | `Read Command Output` |
        | `Should Be Equal` | ${pwd}                | /home/johndoe |
        | `Start Command`   | cd /tmp               |
        | `Start Command`   | pwd                   |
        | ${pwd}=           | `Read Command Output` |
        | `Should Be Equal` | ${pwd}                | /home/johndoe |

        Arguments ``sudo`` and ``sudo_password`` are used for executing
        commands within a sudo session. Due to different permission elevation
        in Cygwin, these two arguments will not when using it.

        | `Start Command`   | pwd                 | sudo=True     |  sudo_password=test |

        `Write` and `Read` can be used for running multiple commands in the
        same shell. See `interactive shells` section for more information.

        This keyword logs the started command with log level ``INFO``.

        ``sudo`` and ``sudo_password`` arguments are new in SSHLibrary 3.0.0.
        """
        sudo = is_truthy(sudo)
        if not sudo:
            self._info("Starting command '%s'." % command)
        else:
            self._info("Starting command 'sudo %s'." % command)
        self._last_command = command
        self.current.start_command(command, sudo, sudo_password)

    def read_command_output(self, return_stdout=True, return_stderr=False,
                            return_rc=False):
        """Returns outputs of the most recent started command.

        At least one command must have been started using `Start Command`
        before this keyword can be used.

        By default, only the standard output of the started command is
        returned:

        | `Start Command`  | echo 'Hello John!'    |
        | ${stdout}=       | `Read Command Output` |
        | `Should Contain` | ${stdout}             | Hello John! |

        Arguments ``return_stdout``, ``return_stderr`` and ``return_rc`` are
        used to specify, what is returned by this keyword.
        If several arguments evaluate to a true value (see `Boolean arguments`),
        multiple values are returned.

        If errors are needed as well, set the argument value to true:

        | `Start Command`   | echo 'Hello John!' |
        | ${stdout}         | ${stderr}=         | `Read Command Output` | return_stderr=True |
        | `Should Be Empty` | ${stderr}          |

        Often checking the return code is enough:

        | `Start Command`               | echo 'Hello John!'    |
        | ${rc}=                        | `Read Command Output` | return_stdout=False | return_rc=True |
        | `Should Be Equal As Integers` | ${rc}                 | 0                   | # succeeded    |

        Using `Start Command` and `Read Command Output` follows
        LIFO (last in, first out) policy, meaning that `Read Command Output`
        operates on the most recent started command, after which that command
        is discarded and its output cannot be read again.

        If several commands have been started, the output of the last started
        command is returned. After that, a subsequent call will return the
        output of the new last (originally the second last) command:

        | `Start Command`  | echo 'HELLO'          |
        | `Start Command`  | echo 'SECOND'         |
        | ${stdout}=       | `Read Command Output` |
        | `Should Contain` | ${stdout}             | 'SECOND' |
        | ${stdout}=       | `Read Command Output` |
        | `Should Contain` | ${stdout}             | 'HELLO'  |

        This keyword logs the read command with log level ``INFO``.
        """
        self._info("Reading output of command '%s'." % self._last_command)
        opts = self._legacy_output_options(return_stdout, return_stderr,
                                           return_rc)
        try:
            stdout, stderr, rc = self.current.read_command_output()
        except SSHClientException as msg:
            raise RuntimeError(msg)
        return self._return_command_output(stdout, stderr, rc, *opts)

    def _legacy_output_options(self, stdout, stderr, rc):
        if not is_string(stdout):
            return stdout, stderr, rc
        stdout = stdout.lower()
        if stdout == 'stderr':
            return False, True, rc
        if stdout == 'both':
            return True, True, rc
        return stdout, stderr, rc

    def _return_command_output(self, stdout, stderr, rc, return_stdout,
                               return_stderr, return_rc):
        self._info("Command exited with return code %d." % rc)
        ret = []
        if is_truthy(return_stdout):
            ret.append(stdout.rstrip('\n'))
        if is_truthy(return_stderr):
            ret.append(stderr.rstrip('\n'))
        if is_truthy(return_rc):
            ret.append(rc)
        if len(ret) == 1:
            return ret[0]
        return ret

    def write(self, text, loglevel=None):
        """Writes the given ``text`` on the remote machine and appends a newline.

        Appended `newline` can be configured.

        This keyword returns and consumes the written ``text``
        (including the appended newline) from the server output. See the
        `Interactive shells` section for more information.

        The written ``text`` is logged. ``loglevel`` can be used to override
        the default `log level`.

        Example:
        | ${written}=          | `Write`         | su                         |
        | `Should Contain`     | ${written}      | su                         | # Returns the consumed output  |
        | ${output}=           | `Read`          |
        | `Should Not Contain` | ${output}       | ${written}                 | # Was consumed from the output |
        | `Should Contain`     | ${output}       | Password:                  |
        | `Write`              | invalidpasswd   |
        | ${output}=           | `Read`          |
        | `Should Contain`     | ${output}       | su: Authentication failure |

        See also `Write Bare`.
        """
        self._write(text, add_newline=True)
        return self._read_and_log(loglevel, self.current.read_until_newline)

    def write_bare(self, text):
        """Writes the given ``text`` on the remote machine without appending a newline.

        Unlike `Write`, this keyword returns and consumes nothing. See the
        `Interactive shells` section for more information.

        Example:
        | `Write Bare`     | su\\n            |
        | ${output}=       | `Read`           |
        | `Should Contain` | ${output}        | su                         | # Was not consumed from output |
        | `Should Contain` | ${output}        | Password:                  |
        | `Write Bare`     | invalidpasswd\\n |
        | ${output}=       | `Read`           |
        | `Should Contain` | ${output}        | su: Authentication failure |

        See also `Write`.
        """
        self._write(text)

    def _write(self, text, add_newline=False):
        try:
            self.current.write(text, is_truthy(add_newline))
        except SSHClientException as e:
            raise RuntimeError(e)

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes the given ``text`` repeatedly until ``expected`` appears in the server output.

        This keyword returns nothing.

        ``text`` is written without appending a newline and is consumed from
        the server output before ``expected`` is read. See more information
        on the `Interactive shells` section.

        If ``expected`` does not appear in output within ``timeout``, this
        keyword fails. ``retry_interval`` defines the time before writing
        ``text`` again. Both ``timeout`` and ``retry_interval`` must be given
        in Robot Framework's time format (e.g. ``5``, ``1 minute``,
        ``2 min 3 s``, ``4.5``) that is explained in detail in the
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|
        User Guide].

        The written ``text`` is logged. ``loglevel`` can be used to override
        the default `log level`.

        This example will write ``lsof -c python27\\n`` (list all files
        currently opened by Python 2.7), until ``myscript.py`` appears in the
        output. The command is written every 0.5 seconds. The keyword fails if
        ``myscript.py`` does not appear in the server output in 5 seconds:

        | `Write Until Expected Output` | lsof -c python27\\n | expected=myscript.py | timeout=5s | retry_interval=0.5s |
        """
        self._read_and_log(loglevel, self.current.write_until_expected, text,
                           expected, timeout, retry_interval)

    def read(self, loglevel=None, delay=None):
        """Consumes and returns everything available on the server output.

        If ``delay`` is given, this keyword waits that amount of time and
        reads output again. This wait-read cycle is repeated as long as
        further reads return more output or the default `timeout` expires.
        ``delay`` must be given in Robot Framework's time format (e.g. ``5``,
        ``4.5s``, ``3 minutes``, ``2 min 3 sec``) that is explained in detail
        in the
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|
        User Guide].

        This keyword is most useful for reading everything from
        the server output, thus clearing it.

        The read output is logged. ``loglevel`` can be used to override
        the default `log level`.

        Example:
        | `Open Connection` | my.server.com |
        | `Login`           | johndoe       | secretpasswd                 |
        | `Write`           | sudo su -     |                              |
        | ${output}=        | `Read`        | delay=0.5s                   |
        | `Should Contain`  | ${output}     | [sudo] password for johndoe: |
        | `Write`           | secretpasswd  |                              |
        | ${output}=        | `Read`        | loglevel=WARN | # Shown in the console due to loglevel |
        | `Should Contain`  | ${output}     | root@                        |

        See `interactive shells` for more information about writing and
        reading in general.
        """
        return self._read_and_log(loglevel, self.current.read, delay)

    def read_until(self, expected, loglevel=None):
        """Consumes and returns the server output until ``expected`` is encountered.

        Text up until and including the ``expected`` will be returned.

        If the `timeout` expires before the match is found, this keyword fails.

        The read output is logged. ``loglevel`` can be used to override
        the default `log level`.

        Example:
        | `Open Connection` | my.server.com |
        | `Login`           | johndoe       | ${PASSWORD}                  |
        | `Write`           | sudo su -     |                              |
        | ${output}=        | `Read Until`  | :                            |
        | `Should Contain`  | ${output}     | [sudo] password for johndoe: |
        | `Write`           | ${PASSWORD}   |                              |
        | ${output}=        | `Read Until`  | @                            |
        | `Should End With` | ${output}     | root@                        |

        See also `Read Until Prompt` and `Read Until Regexp` keywords. For
        more details about reading and writing in general, see the
        `Interactive shells` section.
        """
        return self._read_and_log(loglevel, self.current.read_until, expected)

    def read_until_prompt(self, loglevel=None):
        """Consumes and returns the server output until the prompt is found.

        Text up and until prompt is returned. The `prompt` must be set before
        this keyword is used.

        If the `timeout` expires before the match is found, this keyword fails.

        This keyword is useful for reading output of a single command when
        output of previous command has been read and that command does not
        produce prompt characters in its output.

        The read output is logged. ``loglevel`` can be used to override
        the default `log level`.

        Example:
        | `Open Connection`          | my.server.com       | prompt=$         |
        | `Login`                    | johndoe             | ${PASSWORD}      |
        | `Write`                    | sudo su -           |                  |
        | `Write`                    | ${PASSWORD}         |                  |
        | `Set Client Configuration` | prompt=#            | # For root, the prompt is # |
        | ${output}=                 | `Read Until Prompt` |                  |
        | `Should End With`          | ${output}           | root@myserver:~# |

        See also `Read Until` and `Read Until Regexp` keywords. For more
        details about reading and writing in general, see the `Interactive
        shells` section.
        """
        return self._read_and_log(loglevel, self.current.read_until_prompt)

    def read_until_regexp(self, regexp, loglevel=None):
        """Consumes and returns the server output until a match to ``regexp`` is found.

        ``regexp`` can be a regular expression pattern or a compiled regular
        expression object. See the `Regular expressions` section for more
        details about the syntax.

        Text up until and including the ``regexp`` will be returned.

        If the `timeout` expires before the match is found, this keyword fails.

        The read output is logged. ``loglevel`` can be used to override
        the default `log level`.

        Example:
        | `Open Connection` | my.server.com       |
        | `Login`           | johndoe             | ${PASSWORD}                  |
        | `Write`           | sudo su -           |                              |
        | ${output}=        | `Read Until Regexp` | \\\\[.*\\\\].*:              |
        | `Should Contain`  | ${output}           | [sudo] password for johndoe: |
        | `Write`           | ${PASSWORD}         |                              |
        | ${output}=        | `Read Until Regexp` | .*@                          |
        | `Should Contain`  | ${output}           | root@                        |

        See also `Read Until` and `Read Until Prompt` keywords. For more
        details about reading and writing in general, see the `Interactive
        shells` section.
        """
        return self._read_and_log(loglevel, self.current.read_until_regexp,
                                  regexp)

    def _read_and_log(self, loglevel, reader, *args):
        try:
            output = reader(*args)
        except SSHClientException as e:
            raise RuntimeError(e)
        self._log(output, loglevel)
        return output

    def get_file(self, source, destination='.'):
        """Downloads file(s) from the remote machine to the local machine.

        ``source`` is a path on the remote machine. Both absolute paths and
        paths relative to the current working directory are supported.
        If the source contains wildcards explained in `glob patterns`,
        all files matching it are downloaded. In this case ``destination``
        must always be a directory.

        ``destination`` is the target path on the local machine. Both
        absolute paths and paths relative to the current working directory
        are supported.

        Examples:
        | `Get File` | /var/log/auth.log | /tmp/                      |
        | `Get File` | /tmp/example.txt  | C:\\\\temp\\\\new_name.txt |
        | `Get File` | /path/to/*.txt    |

        The local ``destination`` is created using the rules explained below:

        1. If the ``destination`` is an existing file, the ``source`` file is
           downloaded over it.

        2. If the ``destination`` is an existing directory, the ``source``
           file is downloaded into it. Possible file with the same name is
           overwritten.

        3. If the ``destination`` does not exist and it ends with the path
           separator of the local operating system, it is considered a
           directory. The directory is then created and the ``source`` file
           is downloaded into it. Possible missing intermediate directories
           are also created.

        4. If the ``destination`` does not exist and does not end with the
           local path separator, it is considered a file. The ``source`` file
           is downloaded and saved using that file name, and possible missing
           intermediate directories are also created.

        5. If ``destination`` is not given, the current working directory on
           the local machine is used as the destination. This is typically
           the directory where the test execution was started and thus
           accessible using built-in ``${EXECDIR}`` variable.

        See also `Get Directory`.
        """
        return self._run_sftp_command(self.current.get_file, source,
                                      destination)

    def get_directory(self, source, destination='.', recursive=False):
        """Downloads a directory, including its content, from the remote machine to the local machine.

        ``source`` is a path on the remote machine. Both absolute paths and
        paths relative to the current working directory are supported.

        ``destination`` is the target path on the local machine.  Both
        absolute paths and paths relative to the current working directory
        are supported.

        ``recursive`` specifies whether to recursively download all
        subdirectories inside ``source``. Subdirectories are downloaded if
        the argument value evaluates to true (see `Boolean arguments`).

        Examples:
        | `Get Directory` | /var/logs      | /tmp                |
        | `Get Directory` | /var/logs      | /tmp/non/existing   |
        | `Get Directory` | /var/logs      |
        | `Get Directory` | /var/logs      | recursive=True      |

        The local ``destination`` is created as following:

        1. If ``destination`` is an existing path on the local machine,
           ``source`` directory is downloaded into it.

        2. If ``destination`` does not exist on the local machine, it is
           created and the content of ``source`` directory is downloaded
           into it.

        3. If ``destination`` is not given, ``source`` directory is
           downloaded into the current working directory on the local
           <machine. This is typically the directory where the test execution
           was started and thus accessible using the built-in ``${EXECDIR}``
           variable.

        See also `Get File`.
        """
        return self._run_sftp_command(self.current.get_directory, source,
                                      destination, is_truthy(recursive))

    def put_file(self, source, destination='.', mode='0744', newline=''):
        """Uploads file(s) from the local machine to the remote machine.

        ``source`` is the path on the local machine. Both absolute paths and
        paths relative to the current working directory are supported.
        If the source contains wildcards explained in `glob patterns`,
        all files matching it are uploaded. In this case ``destination``
        must always be a directory.

        ``destination`` is the target path on the remote machine. Both
        absolute paths and paths relative to the current working directory
        are supported.

        ``mode`` can be used to set the target file permission.
        Numeric values are accepted. The default value is ``0744``
        (``-rwxr--r--``).

        ``newline`` can be used to force the line break characters that are
        written to the remote files. Valid values are ``LF`` and ``CRLF``.

        Examples:
        | `Put File` | /path/to/*.txt          |
        | `Put File` | /path/to/*.txt          | /home/groups/robot | mode=0770 |
        | `Put File` | /path/to/*.txt          | newline=CRLF       |

        The remote ``destination`` is created as following:

        1. If ``destination`` is an existing file, ``source`` file is uploaded
           over it.

        2. If ``destination`` is an existing directory, ``source`` file is
           uploaded into it. Possible file with same name is overwritten.

        3. If ``destination`` does not exist and it ends with the
           `path separator`, it is considered a directory. The directory is
           then created and ``source`` file uploaded into it.
           Possibly missing intermediate directories are also created.

        4. If ``destination`` does not exist and it does not end with
           the `path separator`, it is considered a file.
           If the path to the file does not exist, it is created.

        5. If ``destination`` is not given, the user's home directory
           on the remote machine is used as the destination.

        See also `Put Directory`.
        """
        return self._run_sftp_command(self.current.put_file, source,
                                      destination, mode, newline)

    def put_directory(self, source, destination='.', mode='0744', newline='',
                      recursive=False):
        """Uploads a directory, including its content, from the local machine to the remote machine.

        ``source`` is the path on the local machine. Both absolute paths and
        paths relative to the current working directory are supported.

        ``destination`` is the target path on the remote machine. Both
        absolute paths and paths relative to the current working directory
        are supported.

        ``mode`` can be used to set the target file permission.
        Numeric values are accepted. The default value is ``0744``
        (``-rwxr--r--``).

        ``newline`` can be used to force the line break characters that are
        written to the remote files. Valid values are ``LF`` and ``CRLF``.

        ``recursive`` specifies whether to recursively upload all
        subdirectories inside ``source``. Subdirectories are uploaded if the
        argument value evaluates to true (see `Boolean arguments`).

        Examples:
        | `Put Directory` | /var/logs | /tmp               |
        | `Put Directory` | /var/logs | /tmp/non/existing  |
        | `Put Directory` | /var/logs |
        | `Put Directory` | /var/logs | recursive=True     |
        | `Put Directory` | /var/logs | /home/groups/robot | mode=0770 |
        | `Put Directory` | /var/logs | newline=CRLF       |

        The remote ``destination`` is created as following:

        1. If ``destination`` is an existing path on the remote machine,
           ``source`` directory is uploaded into it.

        2. If ``destination`` does not exist on the remote machine, it is
           created and the content of ``source`` directory is uploaded into
           it.

        3. If ``destination`` is not given, ``source`` directory is typically
           uploaded to user's home directory on the remote machine.

        See also `Put File`.
        """
        return self._run_sftp_command(self.current.put_directory, source,
                                      destination, mode, newline, is_truthy(recursive))

    def _run_sftp_command(self, command, *args):
        try:
            files = command(*args)
        except SSHClientException as e:
            raise RuntimeError(e)
        for src, dst in files:
            self._info("'%s' -> '%s'" % (src, dst))

    def file_should_exist(self, path):
        """Fails if the given ``path`` does NOT point to an existing file.

        Example:
        | `File Should Exist` | /boot/initrd.img |

        Note that symlinks are followed:
        | `File Should Exist` | /initrd.img | # Points to /boot/initrd.img |
        """
        if not self.current.is_file(path):
            raise AssertionError("File '%s' does not exist." % path)

    def file_should_not_exist(self, path):
        """Fails if the given ``path`` points to an existing file.

        Example:
        | `File Should Not Exist` | /non/existing |

        Note that this keyword follows symlinks. Thus the example fails if
        ``/non/existing`` is a link that points an existing file.
        """
        if self.current.is_file(path):
            raise AssertionError("File '%s' exists." % path)

    def directory_should_exist(self, path):
        """Fails if the given ``path`` does not point to an existing directory.

        Example:
        | `Directory Should Exist` | /usr/share/man |

        Note that symlinks are followed:
        | `Directory Should Exist` | /usr/local/man | # Points to /usr/share/man/ |
        """
        if not self.current.is_dir(path):
            raise AssertionError("Directory '%s' does not exist." % path)

    def directory_should_not_exist(self, path):
        """Fails if the given ``path`` points to an existing directory.

        Example:
        | `Directory Should Not Exist` | /non/existing |

        Note that this keyword follows symlinks. Thus the example fails if
        ``/non/existing`` is a link that points to an existing directory.
        """
        if self.current.is_dir(path):
            raise AssertionError("Directory '%s' exists." % path)

    def list_directory(self, path, pattern=None, absolute=False):
        """Returns and logs items in the remote ``path``, optionally filtered with ``pattern``.

        ``path`` is a path on the remote machine. Both absolute paths and
        paths relative to the current working directory are supported.
        If ``path`` is a symlink, it is followed.

        Item names are returned in case-sensitive alphabetical order,
        e.g. ``['A Name', 'Second', 'a lower case name', 'one more']``.
        Implicit directories ``.`` and ``..`` are not returned. The returned
        items are automatically logged.

        By default, the item names are returned relative to the given
        remote path (e.g. ``file.txt``). If you want them be returned in the
        absolute format (e.g. ``/home/johndoe/file.txt``), set the
        ``absolute`` argument to any non-empty string.

        If ``pattern`` is given, only items matching it are returned. The
        pattern is a glob pattern and its syntax is explained in the
        `Pattern matching` section.

        Examples (using also other `List Directory` variants):
        | @{items}= | `List Directory`          | /home/johndoe |
        | @{files}= | `List Files In Directory` | /tmp          | *.txt | absolute=True |

        If you are only interested in directories or files,
        use `List Files In Directory` or `List Directories In Directory`,
        respectively.
        """
        try:
            items = self.current.list_dir(path, pattern, is_truthy(absolute))
        except SSHClientException as msg:
            raise RuntimeError(msg)
        self._info('%d item%s:\n%s' % (len(items), plural_or_not(items),
                                       '\n'.join(items)))
        return items

    def list_files_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only files."""
        absolute = is_truthy(absolute)
        try:
            files = self.current.list_files_in_dir(path, pattern, absolute)
        except SSHClientException as msg:
            raise RuntimeError(msg)
        files = self.current.list_files_in_dir(path, pattern, absolute)
        self._info('%d file%s:\n%s' % (len(files), plural_or_not(files),
                                       '\n'.join(files)))
        return files

    def list_directories_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only directories."""
        try:
            dirs = self.current.list_dirs_in_dir(path, pattern, is_truthy(absolute))
        except SSHClientException as msg:
            raise RuntimeError(msg)
        self._info('%d director%s:\n%s' % (len(dirs),
                                           'y' if len(dirs) == 1 else 'ies',
                                           '\n'.join(dirs)))
        return dirs


class _DefaultConfiguration(Configuration):

    def __init__(self, timeout, newline, prompt, loglevel, term_type, width,
                 height, path_separator, encoding):
        super(_DefaultConfiguration, self).__init__(
            timeout=TimeEntry(timeout),
            newline=NewlineEntry(newline),
            prompt=StringEntry(prompt),
            loglevel=LogLevelEntry(loglevel),
            term_type=StringEntry(term_type),
            width=IntegerEntry(width),
            height=IntegerEntry(height),
            path_separator=StringEntry(path_separator),
            encoding=StringEntry(encoding)
        )
