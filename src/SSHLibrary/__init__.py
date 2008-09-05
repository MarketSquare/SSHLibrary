#  Copyright 2008 Nokia Siemens Networks Oyj
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
import string
import re
from types import TupleType, StringTypes

from robot import utils

if utils.is_jython:
    from javaclient import SSHClient
else:
    from pythonclient import SSHClient
    

class SSHLibrary:
    """SSHLibrary is a test library for Robot Framework that enables 
    executing commands over SSH connection.
    
    SSHLibrary works with both Python and Jython interpreters.
    To use SSHLibrary with Python, you must first install paramiko SSH 
    implementation[1] for Python and it's dependencies.
    To use SSHLibrary with Jython, you must have jar distribution of trilead SSH 
    implementation[2] in the Classpath during test execution
    
    [1] http://www.lag.net/paramiko/
    [2] http://www.trilead.com/Products/Trilead_SSH_for_Java/
    
    Currently, there are two modes of operation:
    
    1. When keyword `Execute Command` or `Start Command` is used to execute 
    something, a new channel is opened over the SSH connection. In practice it
    means that no session information is stored. 
    
    2. Keywords `Write` and `Read XXX` operate in an interactive shell, which 
    means that changes to state are visible to next keywords.
    Note that in interactive mode, a prompt must be set before using any of the
    Write-keywords. Prompt can be set either when the library is taken into use
    or when a new connection is opened using `Open Connection`, or using keyword
    `Set Prompt`.
    
    Both modes require that a connection is opened with `Open Connection`.
    """
    ROBOT_LIBRARY_SCOPE="GLOBAL"

    def __init__(self, timeout=3, newline='LF', prompt=None):
        self.cache = utils.ConnectionCache()
        self.client = None
        self._newline = self._parse_newline(newline and newline or 'LF')
        self._timeout = timeout and int(timeout) or 3
        self._default_log_level = 'INFO'
        self._prompt = prompt
        
    def open_connection(self, host, alias=None, port=22, timeout=None, 
                        newline=None, prompt=None):
        """Opens a new SSH connection to given `host` and `port`.
    
        Possible already opened connections are cached.

        Returns the index of this connection which can be used later to switch
        back to it. Index starts from 1 and is reset back to it when `Close All`
        keyword is used.

        Optional `alias` is a name for the connection and it can be used for
        switching between connections similarly as the index. See `Switch
        Connection` for more details about that.
        
        For more information about `timeout`, `newline` and `prompt`, see 
        `Set Timeout`, `Set Newline` and `Set Prompt`, respectively.

        Examples:
        | Open Connection | myhost.net      |            |                     |                     |                  |
        | Open Connection | yourhost.com    | 2nd conn   | # alias             |                     |                  |
        | ${id} =         | Open Connection | myhost.net | # index to variable |                     |                  |
        | ${id} =         | Open Connection | myhost.net | ${None}             | 23                  | # index and port |
        | Open Connection | myhost.net      | 3rd conn   | 25                  | # alias and port    |                  |
        """
        self._host, self._port = host, port
        self._timeout = timeout and int(timeout) or self._timeout
        self._newline = newline and self._parse_newline(newline) or self._newline
        self._prompt = prompt and prompt or self._prompt
        self.client = SSHClient(host, int(port))
        return self.cache.register(self.client, alias)

    def switch_connection(self, index_or_alias):
        """Switches between active connections using index or alias.

        Index is got from `Open Connection` and alias can be given to it.

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
        self.client=self.cache.switch(index_or_alias)

    def close_all_connections(self):
        """Closes all open connections and empties the connection cache.

        After this keyword new indexes get from `Open Connection` are reset to 1.

        This keyword ought to be used in test or suite teardown to make sure
        all connections are closed.
        """
        try:
            self.cache.close_all()
        except AttributeError:
            pass
        self.client = None
        
    def close_connection(self):
        """Closes the currently active connection.
        """
        self.client.close()

    def login(self, username, password):
        """Logs in to SSH server with given user information.

        Example:
        | Login | john | secret |
        """
        self._info("Logging into '%s:%s' with username '%s' and password '%s'" 
                   % (self._host, self._port, username, password))
        self.client.login(username, password)

    def execute_command(self, command, ret_mode='stdout'):
        """Executes command on remote host over existing SSH connection and returns stdout and/or stderr.
    
        This keyword waits until the command is completed. If non-blocking 
        behavior is required, use `Start Command` instead.
        
        Examples:
        | ${out}=   | Execute Command | some command    |              | #stdout is returned |                                 |
        | ${err}=   | Execute Command | some command    | stderr       | #stderr is returned |                                 |
        | ${out}    | ${err}=         | Execute Command | some command | both                | #stdout and stderr are returned |
        """
        self._info("Executing command '%s'" % command)
        return self._process_output(self.client.execute_command(command, ret_mode))

    def start_command(self, command):
        """Starts command execution on remote host over existing SSH connection.
    
        This keyword doesn't return anything. Use `Read Command Output` to read 
        the output generated from command execution.
        
        Note that the `Read Command Output` keyword always reads the output of 
        the most recently started command.
        
        Example:
        | Start Command | some command |
        """
        self._info("Starting command '%s'" % command)
        self._command = command
        self.client.start_command(command)

    def read_command_output(self, ret_mode='stdout'):
        """Reads and returns/logs everything currently available on the output (stdout and/or stderr).

        Examples:
        | ${out}= | Read Command Output |                     |                     |                                 |
        | ${err}= | Read Command Output | stderr              | #stderr is returned |                                 |
        | ${out}  | ${err}=             | Read Command Output | both                | #stdout and stderr are returned |
        """
        self._info("Reading output of command '%s'" % self._command)
        return self._process_output(self.client.read_command_output(ret_mode))
            
    def _process_output(self, output):
        if type(output) == TupleType:
            return [self._strip_possible_newline(out) for out in output]
        return self._strip_possible_newline(output)
        
    def _strip_possible_newline(self, output):
        if output.endswith('\n'):
            return output[:-1]
        return output
        
    def set_timeout(self, timeout):
        """Sets the timeout used in read operations to given value.

        `timeout` is given in Robot Framework's time format 
        (e.g. 1 minute 20 seconds).

        The read operations of keywords `Read Until`, `Read Until Prompt`, 
        `Read Until Regexp` and `Write Until Expected Output` will try to read 
        the output until either the expected text appears in the output or the
        timeout expires. For commands that take long time to produce their 
        output, this timeout must be set properly. 
        
        Old timeout is returned and it can be used to restore it later.
        
        Example:
        | ${tout} = | Set Timeout | 2 minute 30 seconds |
        | Do Something |
        | Set Timeout | ${tout} |
        """
        old = self._timeout
        self._timeout = utils.timestr_to_secs(timeout)
        return utils.secs_to_timestr(old)
        
    def set_newline(self, newline):
        """Sets the newline used by `Write` keyword.
        
        Old newline is returned and it can be used to restore it later.
        See `Set Timeout` for an example. 
        """
        old = self._newline
        self._newline = self._parse_newline(newline)
        return old
    
    def _parse_newline(self, newline):
        return newline.upper().replace('LF','\n').replace('CR','\r')

    def set_prompt(self, prompt):
        """Sets the prompt used by `Read Until Prompt` keyword.
        
        Old prompt is returned and it can be used to restore it later.
        
        Example:
        | ${prompt} | Set Prompt | $ | 
        | Do Something |
        | Set Prompt | ${prompt} | 
        """
        old = hasattr(self, '_prompt') and self._prompt or ''
        self._prompt = prompt
        return old
    
    def set_default_log_level(self, level):
        """Sets the default log level used by all read keywords.
        
        The possible values are TRACE, DEBUG, INFO and WARN. The default is
        INFO. The old value is returned and can be used to restore it later,
        similarly as with `Set Timeout`.
        """
        self._is_valid_log_level(level, raise_if_invalid=True)
        old = self._default_log_level
        self._default_log_level = level.upper()
        return old
    
    def write(self, text, loglevel=None):
        """Writes given text over the connection and appends newline.
        
        Consumes the written text (until the appended newline) from output 
        and returns it. Given text must not contain newlines.
        
        Note: This keyword does not return the possible output of the executed 
        command. To get the output, one of the `Read XXX` keywords must be 
        used.
        """
        self.write_bare(text + self._newline)
        data = self.read_until(self._newline, loglevel)
        return data

    def write_bare(self, text):
        """Writes given text over the connection without appending newline"""
        try:
            text = str(text)
        except UnicodeError:
            raise ValueError('Only ascii characters are allowed in SSH.' 
                             'Got: %s' % text)
        self._info("Writing %s" % repr(text))
        if self._prompt is None:
            msg = ("Using 'Write' or 'Write Bare' keyword requires setting "
                   "prompt first. Prompt can be set either when taking library "
                   "into use or when using 'Open Connection' keyword.")
            raise RuntimeError(msg)
        self.client.write(text, self._prompt)

    def read(self, loglevel=None):
        """Reads and returns/logs everything currently available on the output.

        Read message is always returned and logged. Default log level is 
        either 'INFO', or the level set with `Set Default Log Level`.
        `loglevel` can be used to override the default log level, and available
        levels are TRACE, DEBUG, INFO and WARN.
        """
        ret = self.client.read()
        self._log(ret, loglevel)
        return ret

    def read_until(self, expected, loglevel=None):
        """Reads from the current output until expected is encountered or timeout expires.

        Text up until and including the match will be returned, If no match is
        found, the keyword fails.
        
        The timeout is by default three seconds but can be changed using 
        `Set Timeout` keyword.
        
        See `Read` for more information on `loglevel`.
        """
        ret = self.client.read_until(expected, self._timeout)
        self._log(ret, loglevel)
        if not ret.endswith(expected):
            raise AssertionError("No match found for '%s' in %s" 
                                 % (expected, utils.secs_to_timestr(self._timeout)))
        return ret

    def read_until_regexp(self, regexp, loglevel=None):
        """Reads from the current output until a match to `regexp` is found or timeout expires.

        `regexp` can be a pattern or a compiled re-object.
        
        Returns text up until and including the regexp.

        The timeout is by default two seconds but can be changed using 
        `Set Timeout` keyword.
        
        See `Read` for more information on `loglevel`.
        Examples:
        | Read Until Regexp | (#|$) |
        | Read Until Regexp | some regexp  | DEBUG |
        """
        ret = self.client.read_until_regexp(regexp, self._timeout)
        self._log(ret, loglevel)
        return ret

    def read_until_prompt(self, loglevel=None):
        """Reads and returns text from the current output until prompt is found.
        
        Prompt must have been set, either in Library import or by using 
        `Set Prompt` -keyword.
        
        See `Read` for more information on `loglevel`.
        """
        if not self._prompt:
            raise RuntimeError('Prompt is not set')
        return self.read_until(self._prompt, loglevel)

        
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
        starttime = time.time()
        while time.time() - starttime < timeout:
            self.write(text)
            ret = self.client.read_until(expected, retry_interval)
            self._log(ret, loglevel)
            if ret.endswith(expected):
                return ret
        raise AssertionError("No match found for '%s' in %s" 
                             % (expected, utils.secs_to_timestr(timeout)))
        
    def _info(self, msg):
        self._log(msg, 'INFO')
        
    def _log(self, msg, level=None):
        self._is_valid_log_level(level, raise_if_invalid=True)
        msg = msg.strip()
        if level is None:
            level = self._default_log_level
        if msg != '':
            print '*%s* %s' % (level.upper(), msg)

    def _is_valid_log_level(self, level, raise_if_invalid=False):
        if level is None:
            return True
        if type(level) in StringTypes and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN']:
            return True
        if not raise_if_invalid:
            return False
        raise AssertionError("Invalid log level '%s'" % level)
    
    def put_file(self, source, destination='.', mode='0744'):
        """Copies file(s) from local host to remote host using existing SSH connection.

        1. If the destination is an existing file, the source file is copied
        over it.
        2. If the destination is an existing directory, the source file is
        copied into it. Possible file with same name is overwritten.
        3. If the destination does not exist and it ends with path separator ('/'), 
        it is considered a directory. That directory is created and source file 
        copied into it. Possibly missing intermediate directories are also created.
        4. If the destination does not exist and it does not end with path
        separator, it is considered a file. If the path to the file does not
        exist it is created.
        5. By default, destination is empty and the user's home directory in the
        remote machine is used as destination.
        
        Using wild cards like '*' and '?' are allowed.
        When wild cards are used, destination MUST be a directory and only files
        are copied from the source, sub directories are ignored. If the contents 
        of sub directories are also needed, use the keyword again.
        Default file permission is 0744 (-rwxr--r--) and can be changed by
        giving a value to the optional `mode` parameter.
        
        Examples:

        | Put File | /path_to_local_file/local_file.txt | /path_to_remote_file/remote_file.txt | # single file                    |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               | # multiple files with wild cards |                    |
        | Put File | /path_to_local_files/*.txt         | /path_to_remote_files/               |  0777                            | # file permissions |
        
        """
        self.client.put_file(source, destination, int(mode,8))

    def get_file(self, source, destination='.'):
        """Copies a file from remote host to local host using existing SSH connection.

        1. If the destination is an existing file, the source file is copied
        over it.
        2. If the destination is an existing directory, the source file is
        copied into it. Possible file with same name is overwritten.
        3. If the destination does not exist and it ends with path separator 
        ('/' in unixes, '\\' in Windows), it is considered a directory. That 
        directory is created and source file copied into it. Possible missing
        intermediate directories are also created.
        4. If the destination does not exist and it does not end with path
        separator, it is considered a file. If the path to the file does not
        exist it is created.
        5. By default, destination is empty, and in that case the current working
        directory in the local machine is used as destination. This will most 
        probably be the directory where test execution was started.

        Using wild cards like '*' and '?' are allowed.
        When wild cards are used, destination MUST be a directory and only files
        are copied from the source, sub directories are ignored. If the contents 
        of sub directories are also needed, use the keyword again.
        
        Examples:

        | Get File | /path_to_remote_file/remote_file.txt | /path_to_local_file/local_file.txt | # single file                    |
        | Get File | /path_to_remote_files/*.txt          | /path_to_local_files/              | # multiple files with wild cards |
        
        """
        self.client.get_file(source, destination)
        