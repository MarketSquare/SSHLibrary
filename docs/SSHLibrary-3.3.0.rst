================
SSHLibrary 3.3.0
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.3.0 is a new release with SCP support and a few smaller
fixes and enhancements.
All issues targeted for SSHLibrary v3.3.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.3.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.3.0 was released on Tuesday February 19, 2019.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.3.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The most important feature is the support for SCP (`#137`_). It can be enabled by setting the
`scp` argument to `TRANSFER` or `ALL` (if SFTP is disabled entirely).

Acknowledgements
================

Thank you @p74 and @mtango for helping with testing and feedback for the pre-release versions!

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#137`_
      - enhancement
      - high
      - Support for SCP
    * - `#284`_
      - bug
      - medium
      - Index handling issue for multiple connections 
    * - `#299`_
      - enhancement
      - medium
      - Add posibility to restrict binding to specific interface when using tunneling
    * - `#297`_
      - bug
      - low
      - `Put Directory` issue with Windows path destination
    * - `#283`_
      - enhancement
      - low
      - Read SSH hostnames from ~/.ssh/config

Altogether 5 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.3.0>`__.

.. _#137: https://github.com/MarketSquare/SSHLibrary/issues/137
.. _#284: https://github.com/MarketSquare/SSHLibrary/issues/284
.. _#299: https://github.com/MarketSquare/SSHLibrary/issues/299
.. _#297: https://github.com/MarketSquare/SSHLibrary/issues/297
.. _#283: https://github.com/MarketSquare/SSHLibrary/issues/283
