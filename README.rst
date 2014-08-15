SSHLibrary for Robot Framework
==============================

Introduction
------------

SSHLibrary is a `Robot Framework <http://robotframework.org>`__ test
library for testing SSH and SFTP. It works both with Python and Jython.

The library has the following main usages:

- Executing commands on the remote machine, either with blocking or
  non-blocking behaviour.
- Writing and reading in an interactive shell.
- Transferring files and directories over SFTP.
- Ensuring that files and directories exist on the remote machine.

SSHLibrary is open source software licensed under `Apache License 2.0
<http://www.apache.org/licenses/LICENSE-2.0.html>`__.

Installation
------------

SSHLibrary itself can be installed using `pip <http://pip-installer.org>`__::

    pip install robotframework-sshlibrary

If you use SSHLibrary on Python, you will also need to install `paramiko
<http://paramiko.org>`__ SSH module. Similarly with Jython you need Trilead
SSH JAR distribution. See `INSTALL.rst`__ for more details.

.. Using full URL here to make it work also on PyPI
__ https://github.com/robotframework/SSHLibrary/blob/master/INSTALL.rst

Documentation
-------------

Keyword documentation by version can be found from
http://robotframework.org/SSHLibrary/.

For general information about using test libraries with Robot Framework, see
`Robot Framework User Guide`__.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#using-test-libraries
