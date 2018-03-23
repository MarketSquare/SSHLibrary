SSHLibrary
===============

.. contents::

Introduction
------------

SSHLibrary_ is a `Robot Framework`_ test
library for SSH and SFTP.  The project is hosted on GitHub_
and downloads can be found from PyPI_.

SSHLibrary is operating system independent and supports Python 2.7 as well
as Python 3.4 or newer. In addition to the normal Python_ interpreter,
it also works with `Jython 2.7`_.

The library has the following main usages:

- Executing commands on the remote machine, either with blocking or
  non-blocking behavior.
- Writing and reading in an interactive shell.
- Transferring files and directories over SFTP.
- Ensuring that files and directories exist on the remote machine.

.. image:: https://img.shields.io/pypi/l/robotframework-sshlibrary.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0

.. image:: https://api.travis-ci.org/robotframework/SSHLibrary.png
   :target: http://travis-ci.org/robotframework/SSHLibrary

Documentation
-------------

See `keyword documentation`_ for available keywords and more information
about the library in general.

For general information about using test libraries with Robot Framework, see
`Robot Framework User Guide`_.

Installation
------------

The recommended installation method is using pip_::

    pip install --upgrade robotframework-sshlibrary

Running this command installs also the latest Robot Framework and paramiko_
versions. The minimum supported paramiko version is ``1.15.0``.
The ``--upgrade`` option can be omitted when installing the library for the
first time.

With recent versions of ``pip`` it is possible to install directly from the
GitHub_ repository. To install latest source from the master branch, use
this command::

    pip install git+https://github.com/robotframework/SSHLibrary.git

Alternatively you can download the source distribution from PyPI_, extract
it, and install it using one of the following depending are you using
Python or Jython::

    python setup.py install
    jython setup.py install

A benefit of using pip is that it automatically installs paramiko
and Cryptography_ modules (or PyCrypto_ if paramiko version < 2.0)
that SSHLibrary requires on Python.

On Jython, SSHLibrary requires Trilead SSH JAR distribution. You need to download
`Trilead SSH JAR distribution`_ and add it to CLASSPATH.

Usage
-----

To use SSHLibrary in Robot Framework tests, the library needs to first be
imported using the Library setting as any other library.

When using Robot Framework, it is generally recommended to write as
easy-to-understand tests as possible. The keywords provided by
SSHLibrary are pretty low level and it is typically a good idea to
write tests using Robot Framework's higher level keywords that utilize
SSHLibrary keywords internally. This is illustrated by the following example
where SSHLibrary keywords like ``Open Connection`` and ``Login`` are grouped
together in a higher level keyword like ``Open Connection And Log In``.

.. code:: robotframework

    *** Settings ***
    Documentation          This example demonstrates executing a command on a remote machine
    ...                    and getting its output.
    ...
    ...                    Notice how connections are handled as part of the suite setup and
    ...                    teardown. This saves some time when executing several test cases.

    Library                SSHLibrary
    Suite Setup            Open Connection And Log In
    Suite Teardown         Close All Connections

    *** Variables ***
    ${HOST}                localhost
    ${USERNAME}            test
    ${PASSWORD}            test

    *** Test Cases ***
    Execute Command And Verify Output
        [Documentation]    Execute Command can be used to run commands on the remote machine.
        ...                The keyword returns the standard output by default.
        ${output}=         Execute Command    echo Hello SSHLibrary!
        Should Be Equal    ${output}          Hello SSHLibrary!

    *** Keywords ***
    Open Connection And Log In
       Open Connection     ${HOST}
       Login               ${USERNAME}        ${PASSWORD}

Support
-------

If the provided documentation is not enough, there are various support forums
available:

- `robotframework-users`_ mailing list
- ``#sshlibrary`` and ``#sshlibrary-dev`` channels in
  Robot Framework `Slack community`_
- SSHLibrary `issue tracker`_ for bug reports and concrete enhancement
  requests
- `Other support forums`_ including paid support

.. _Robot Framework: http://robotframework.org
.. _Robot Framework User Guide: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#using-test-libraries
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _GitHub: https://github.com/robotframework/SSHLibrary
.. _Python: http://python.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _Keyword Documentation: http://robotframework.org/SSHLibrary/SSHLibrary.html
.. _Jython 2.7: http://jython.org
.. _paramiko: http://www.paramiko.org
.. _Cryptography: https://cryptography.io
.. _PyCrypto: http://www.pycrypto.org
.. _Trilead SSH JAR distribution: http://search.maven.org/remotecontent?filepath=com/trilead/trilead-ssh2/1.0.0-build221/trilead-ssh2-1.0.0-build221.jar
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack community: https://robotframework-slack-invite.herokuapp.com
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues
.. _Other support forums: http://robotframework.org/#support