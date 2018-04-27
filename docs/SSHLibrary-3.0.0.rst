================
SSHLibrary 3.0.0
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.0.0  is a new release with Python 3 support and
other fixes and enhancements.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.0.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.0.0 was released on Friday April 27, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.0.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The main new feature in SSHLibrary 3.0.0 is the support for Python 3. The supported interpreters are Python 2.7, Python 3.4+ and Jython 2.7 (`#219`_).

Another important feature is the possibility to use sudo to execute and start commands (`#189`_).

The keyword documentation has been improved (`#223`_).

Backwards incompatible changes
==============================

New arguments were added to `Login with Public Key` keyword and `delay` must be provided as a named argument (`#146`_).

Acknowledgements
================

Thanks to `@rainmanwy <https://github.com/rainmanwy>`_ for the Python 3
pull request (`#207`_) and also others who provided earlier PRs related
to it.

Big thanks also to `Mihai Pârvu <https://github.com/mihaiparvu>`_,
`Oana Brinzan <https://github.com/oanab11>`_ and
`Andreea Kovacs <https://github.com/andreeakovacs>`_ for their work and
especially for promising to work as SSHLibrary maintainers!

.. _#207: https://github.com/robotframework/SSHLibrary/pull/207

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#219`_
      - enhancement
      - critical
      - Python 3 compatibility
    * - `#189`_
      - enhancement
      - high
      - sudo for  "Execute Command" and "Start Command" 
    * - `#223`_
      - enhancement
      - high
      - Enhance keyword documentation
    * - `#182`_
      - bug
      - medium
      - 'Put Directory' command doesn't upload correctly the files with ':' in the name.
    * - `#146`_
      - enhancement
      - medium
      - Login using agent forwarding
    * - `#199`_
      - enhancement
      - medium
      - Support regexp for connection prompt
    * - `#201`_
      - enhancement
      - medium
      - Add support for Travis CI
    * - `#132`_
      - enhancement
      - low
      - Capture the pre login banner
    * - `#174`_
      - enhancement
      - low
      - Enhance acceptance tests to cover IPv6

Altogether 9 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.0.0>`__.

.. _#219: https://github.com/robotframework/SSHLibrary/issues/219
.. _#189: https://github.com/robotframework/SSHLibrary/issues/189
.. _#223: https://github.com/robotframework/SSHLibrary/issues/223
.. _#182: https://github.com/robotframework/SSHLibrary/issues/182
.. _#146: https://github.com/robotframework/SSHLibrary/issues/146
.. _#199: https://github.com/robotframework/SSHLibrary/issues/199
.. _#201: https://github.com/robotframework/SSHLibrary/issues/201
.. _#132: https://github.com/robotframework/SSHLibrary/issues/132
.. _#174: https://github.com/robotframework/SSHLibrary/issues/174
