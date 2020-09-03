====================================
SSHLibrary 3.5.0 Release Candidate 1
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.5.0rc1 is a new release with
jump-host functionality and other enhancements and bug fixes.
All issues targeted for SSHLibrary v3.5.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.5.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.5.0rc1 was released on Thursday September 3, 2020.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.5.0


.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Big thank you to the following contributors from the community:

- @freddebacker for SSHLibrary.Read Until with command which produces long output (`#151`_, rc 1)
- @jsdobkin for Jump host functionality (`#356`_, rc 1)
- @tirkarthi for Deprecation warning due to invalid escape sequences in Python 3.7 (`#341`_, rc 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#151`_
      - enhancement
      - high
      -  SSHLibrary.Read Until with command which produces long output
      - rc 1
    * - `#349`_
      - bug
      - medium
      - Incorrect Read Command Output INFO Message for Multiple Connections
      - rc 1
    * - `#121`_
      - enhancement
      - medium
      - "Open Connection" allows duplicate aliases
      - rc 1
    * - `#323`_
      - enhancement
      - medium
      - Add Login With Agent keyword
      - rc 1
    * - `#340`_
      - enhancement
      - medium
      - Get stdout/stderr after Execute Command was interrupted by timeout
      - rc 1
    * - `#348`_
      - enhancement
      - medium
      - Allow showing console output with Execute Command
      - rc 1
    * - `#356`_
      - enhancement
      - medium
      - Jump host functionality
      - rc 1
    * - `#341`_
      - enhancement
      - low
      - Deprecation warning due to invalid escape sequences in Python 3.7
      - rc 1

Altogether 8 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.5.0>`__.

.. _#151: https://github.com/robotframework/SSHLibrary/issues/151
.. _#349: https://github.com/robotframework/SSHLibrary/issues/349
.. _#121: https://github.com/robotframework/SSHLibrary/issues/121
.. _#323: https://github.com/robotframework/SSHLibrary/issues/323
.. _#340: https://github.com/robotframework/SSHLibrary/issues/340
.. _#348: https://github.com/robotframework/SSHLibrary/issues/348
.. _#356: https://github.com/robotframework/SSHLibrary/issues/356
.. _#341: https://github.com/robotframework/SSHLibrary/issues/341
