.. list-table::
   :header-rows: 0

   * - Statistic:
     - |_github_created_at|
     - |_pypi_python_version|
     - |_pypi_downloads|
   * - Quality:
     - |_github_main_status|
     - Next Release:
     - |_github_milestone_4|
   * - Pulse:
     - |_github_latest_release|
     - |_github_commits_since_release|
     - |_github_last_commit|

SSHLibrary
===============

.. contents::

Introduction
------------

SSHLibrary_ is a `Robot Framework`_ test
library for SSH and SFTP.  The project is hosted on GitHub_
and downloads can be found from PyPI_.

SSHLibrary is operating system independent and supports Python 3.6 or newer.

The library has the following main usages:

- Executing commands on the remote machine, either with blocking or
  non-blocking behavior.
- Writing and reading in an interactive shell.
- Transferring files and directories over SFTP.
- Ensuring that files and directories exist on the remote machine.

.. image:: https://img.shields.io/pypi/l/robotframework-sshlibrary.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0

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

Running this command installs also the latest Robot Framework, paramiko_
and scp_ versions. The minimum supported paramiko version is ``1.15.3`` and
minimum supported scp version is ``0.13.0``.
The ``--upgrade`` option can be omitted when installing the library for the
first time.

With recent versions of ``pip`` it is possible to install directly from the
GitHub_ repository. To install latest source from the master branch, use
this command::

    pip install git+https://github.com/MarketSquare/SSHLibrary.git

Alternatively you can download the source distribution from PyPI_, extract
it, and install it using one the command::

    python setup.py install

A benefit of using pip is that it automatically installs scp, paramiko
and Cryptography_ modules (or PyCrypto_ if paramiko version < 2.0)
that SSHLibrary requires.

For creating SSH tunnels robotbackgroundlogger_ > 1.2 is also a requirement.

Docker
~~~~~~

When installing SSHLibrary in a container (eg. Alpine Linux) there are more dependencies
that must be installed: gcc_, make_, openssl-dev_, musl-dev_ and libffi-dev_. These
packages can be installed using::

    apk add gcc make openssl-dev musl-dev libffi-dev

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
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _GitHub: https://github.com/MarketSquare/SSHLibrary
.. _Python: http://python.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _Keyword Documentation: https://marketsquare.github.io/SSHLibrary/SSHLibrary.html
.. _Jython 2.7: http://jython.org
.. _paramiko: http://www.paramiko.org
.. _scp: https://github.com/jbardin/scp.py
.. _Cryptography: https://cryptography.io
.. _PyCrypto: http://www.pycrypto.org
.. _robotbackgroundlogger: https://github.com/robotframework/robotbackgroundlogger
.. _gcc: https://pkgs.alpinelinux.org/packages?name=gcc&branch=edge
.. _make: https://pkgs.alpinelinux.org/packages?name=make&branch=edge
.. _openssl-dev: https://pkgs.alpinelinux.org/packages?name=openssl-dev&branch=edge
.. _musl-dev: https://pkgs.alpinelinux.org/packages?name=musl-dev&branch=edge
.. _libffi-dev: https://pkgs.alpinelinux.org/packages?name=libffi-dev&branch=edge
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack community: https://robotframework-slack-invite.herokuapp.com
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues
.. _Other support forums: http://robotframework.org/#support

.. |_github_created_at| image:: https://img.shields.io/github/created-at/MarketSquare/SSHLibrary?logo=robotframework
   :alt: GitHub Created At

.. |_pypi_downloads| image:: https://img.shields.io/pypi/dm/robotframework-sshlibrary
   :alt: PyPI - Downloads

.. |_github_milestone_4| image:: https://img.shields.io/github/milestones/progress-percent/MarketSquare/SSHLibrary/25
   :alt: GitHub milestone details

.. |_pypi_python_version| image:: https://img.shields.io/pypi/pyversions/robotframework-sshlibrary
   :alt: PyPI - Python Version

.. |_github_main_status| image:: https://img.shields.io/github/checks-status/MarketSquare/SSHLibrary/master
   :alt: GitHub branch status

.. |_github_commits_since_release| image:: https://img.shields.io/github/commits-since/MarketSquare/SSHLibrary/latest
   :alt: GitHub commits since latest release

.. |_github_latest_release| image:: https://img.shields.io/github/release-date/MarketSquare/SSHLibrary
   :alt: GitHub Release Date

.. |_github_last_commit| image:: https://img.shields.io/github/last-commit/MarketSquare/SSHLibrary
   :alt: GitHub last commit
