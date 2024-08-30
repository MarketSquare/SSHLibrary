====================================
SSHLibrary 3.4.0 Release Candidate 2
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.4.0rc2 is a new release with
several enhancements and bug fixes.
All issues targeted for SSHLibrary v3.4.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.4.0rc2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.4.0rc2 was released on Wednesday August 21, 2019.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.4.0


.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Thank you all for  your great contributions:

- @StefanMewa: It's possible to switch to already closed connection (`#304`_, rc 1)
- @Noordsestern: [SFTP] `create remote file` fails when server denies chmod command (`#312`_, rc 2)
- @mika-b: Get File attempts to open SFTP connection even when scp=ALL was requested. (`#329`_, rc 2)
- @bachng2017: Login with password fails even with correct credentials (confirmed by sshclient) (`#331`_, rc 2)
- @jsdobkin: Add SSH Agent Forwarding to command execution (`#334`_, rc 2)

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
    * - `#278`_
      - bug
      - low
      - SSH Tunneling does not work on Python 2.7 Windows
      - rc 2
    * - `#292`_
      - bug
      - low
      - Support ANSI escape sequences
      - rc 2
    * - `#312`_
      - bug
      - low
      - [SFTP] `create remote file` fails when server denies chmod command
      - rc 2
    * - `#329`_
      - bug
      - low
      - Get File attempts to open SFTP connection even when scp=ALL was requested.
      - rc 2
    * - `#310`_
      - enhancement
      - low
      - Login using key agent
      - rc 1
    * - `#331`_
      - enhancement
      - low
      - Login with password fails even with correct credentials (confirmed by sshclient)
      - rc 2
    * - `#334`_
      - enhancement
      - low
      - Add SSH Agent Forwarding to command execution
      - rc 2

Altogether 11 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.4.0>`__.

.. _#304: https://github.com/MarketSquare/SSHLibrary/issues/304
.. _#318: https://github.com/MarketSquare/SSHLibrary/issues/318
.. _#243: https://github.com/MarketSquare/SSHLibrary/issues/243
.. _#285: https://github.com/MarketSquare/SSHLibrary/issues/285
.. _#278: https://github.com/MarketSquare/SSHLibrary/issues/278
.. _#292: https://github.com/MarketSquare/SSHLibrary/issues/292
.. _#312: https://github.com/MarketSquare/SSHLibrary/issues/312
.. _#329: https://github.com/MarketSquare/SSHLibrary/issues/329
.. _#310: https://github.com/MarketSquare/SSHLibrary/issues/310
.. _#331: https://github.com/MarketSquare/SSHLibrary/issues/331
.. _#334: https://github.com/MarketSquare/SSHLibrary/issues/334
