================
SSHLibrary 3.4.0
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.4.0 is a new release with
several enhancements and bug fixes.
All issues targeted for SSHLibrary v3.4.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.4.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.4.0 was released on Friday August 30, 2019.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.4.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Some of the most important new features are:
 - Logging mechanism was added when creating tunnels using the `Create Local SSH Tunnel` keyword (`#243`_)
 - Support for SSH subsystem invocation (`#285`_)
 - Support for ANSI escape sequences (`#292`_)
 - Add SSH Agent Forwarding to command execution (`#334`_)
 - Add socket support with ProxyCommand (`#335`_)

Acknowledgements
================

Thank you all for  your great contributions:

- @StefanMewa: It's possible to switch to already closed connection (`#304`_)
- @Noordsestern: [SFTP] `create remote file` fails when server denies chmod command (`#312`_)
- @mika-b: Get File attempts to open SFTP connection even when scp=ALL was requested. (`#329`_)
- @bachng2017: Login with password fails even with correct credentials (confirmed by sshclient) (`#331`_)
- @jsdobkin: Add SSH Agent Forwarding to command execution (`#334`_)
- @bachng2017: Add socket support with ProxyCommand (`#335`_)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#304`_
      - bug
      - medium
      - It's possible to switch to already closed connection
    * - `#318`_
      - bug
      - medium
      - Read output command generates Type Error
    * - `#243`_
      - enhancement
      - medium
      - Create Local Ssh Tunnel keyword gives no info about the success/failure of the Keyword
    * - `#285`_
      - enhancement
      - medium
      - SSH subsystem invocation
    * - `#278`_
      - bug
      - low
      - SSH Tunneling does not work on Python 2.7 Windows
    * - `#292`_
      - bug
      - low
      - Support ANSI escape sequences
    * - `#312`_
      - bug
      - low
      - [SFTP] `create remote file` fails when server denies chmod command
    * - `#329`_
      - bug
      - low
      - Get File attempts to open SFTP connection even when scp=ALL was requested.
    * - `#310`_
      - enhancement
      - low
      - Login using key agent
    * - `#331`_
      - enhancement
      - low
      - Login with password fails even with correct credentials (confirmed by sshclient)
    * - `#333`_
      - bug
      - high
      - `Write` keyword hangs in teardown if authentication failed
    * - `#334`_
      - enhancement
      - low
      - Add SSH Agent Forwarding to command execution
    * - `#335`_
      - enhancement
      - low
      - Add socket support with ProxyCommand

Altogether 13 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.4.0>`__.

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
.. _#333: https://github.com/MarketSquare/SSHLibrary/issues/333
.. _#334: https://github.com/MarketSquare/SSHLibrary/issues/334
.. _#335: https://github.com/MarketSquare/SSHLibrary/issues/335
