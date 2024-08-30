========================
SSHLibrary 3.0.1 alpha 1
========================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.0.1 alpha 1 is a new release with local ssh tunneling
support and few smaller fixes.
All issues targeted for SSHLibrary v3.0.1 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.0.1a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.0.1a1 was released on Friday June 8, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.0.1


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The most important feature in SSHLibrary 3.0.1 is the support for
local port forwarding (SSH tunneling) (`#224`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#230`_
      - bug
      - high
      - Command is terminated after 0.1 seconds when sudo_password is used
      - alpha 1
    * - `#224`_
      - enhancement
      - high
      - Implement creation of SSH tunnels with Paramiko
      - alpha 1
    * - `#206`_
      - enhancement
      - medium
      - Command execution should take into account user configurable timeout
      - alpha 1

Altogether 3 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.0.1>`__.

.. _#230: https://github.com/MarketSquare/SSHLibrary/issues/230
.. _#224: https://github.com/MarketSquare/SSHLibrary/issues/224
.. _#206: https://github.com/MarketSquare/SSHLibrary/issues/206
