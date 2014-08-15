SSHLibrary for Robot Framework
==============================

Introduction
------------

SSHLibrary is a `Robot Framework <http://robotframework.org>`__ test
library for testing SSH and SFTP. It is operating system independent
and works both with Python and Jython.

The library has the following main usages:

- Executing commands on the remote machine, either with blocking or
  non-blocking behavior.
- Writing and reading in an interactive shell.
- Transferring files and directories over SFTP.
- Ensuring that files and directories exist on the remote machine.

SSHLibrary is open source software licensed under `Apache License 2.0
<http://www.apache.org/licenses/LICENSE-2.0.html>`__.

Installation
------------

When installing SSHLibrary on UNIX-like machines with Python, the easiest
approach is using `pip <http://pip-installer.org>`__::

    pip install robotframework-sshlibrary

Alternatively you can download the source distribution from `PyPI
<https://pypi.python.org/pypi/robotframework-sshlibrary>`__, extract
it, and install it using one of the following depending are you using
Python or Jython::

    python setup.py install
    jython setup.py install

A benefit of using pip is that it automatically installs `paramiko
<http://paramiko.org>`__ and `PyCrypto <http://pycrypto.org>`__
modules that SSHLibrary requires on Python. Using pip on Windows with
Python works too, but you need to first install PyCrypto module
manually.

On Jython SSHLibrary requires Trilead SSH JAR distribution.

For more detailed installation instructions see `INSTALL.rst`__.

.. Using full URL here to make it work also on PyPI
__ https://github.com/robotframework/SSHLibrary/blob/master/INSTALL.rst

Documentation
-------------

Keyword documentation by version can be found from
http://robotframework.org/SSHLibrary/.

For general information about using test libraries with Robot Framework, see
`Robot Framework User Guide`__.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#using-test-libraries
