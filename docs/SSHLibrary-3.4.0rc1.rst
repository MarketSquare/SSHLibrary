====================================
SSHLibrary 3.4.0 Release Candidate 1
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.4.0 Release Candidate 1 is a new release with
several enhancements and bug fixes.
All issues targeted for SSHLibrary v3.4.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.4.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.4.0rc1 was released on Tuesday July 30, 2019.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.4.0


.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Thank you, @StefanMewa for your great contribution to:

- It's possible to switch to already closed connection (`#304`_, rc 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#304`_
      - bug
      - medium
      - It's possible to switch to already closed connection
      - rc 1
    * - `#318`_
      - bug
      - medium
      - Read output command generates Type Error
      - rc 1
    * - `#243`_
      - enhancement
      - medium
      - Create Local Ssh Tunnel keyword gives no info about the success/failure of the Keyword
      - rc 1
    * - `#285`_
      - enhancement
      - medium
      - SSH subsystem invocation
      - rc 1
    * - `#292`_
      - bug
      - low
      - Strange chars are added at the end of a line
      - rc 1
    * - `#310`_
      - enhancement
      - low
      - Login using key agent
      - rc 1

Altogether 6 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.4.0>`__.

.. _#304: https://github.com/robotframework/SSHLibrary/issues/304
.. _#318: https://github.com/robotframework/SSHLibrary/issues/318
.. _#243: https://github.com/robotframework/SSHLibrary/issues/243
.. _#285: https://github.com/robotframework/SSHLibrary/issues/285
.. _#292: https://github.com/robotframework/SSHLibrary/issues/292
.. _#310: https://github.com/robotframework/SSHLibrary/issues/310
