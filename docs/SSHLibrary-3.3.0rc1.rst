====================================
SSHLibrary 3.3.0 Release Candidate 1
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.3.0 Realease Candidate 1 is a new release with
SCP support and a few smaller fixes and enhancements.
All issues targeted for SSHLibrary v3.3.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.3.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.3.0rc1 was released on Wednesday February 13, 2019.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.3.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The target of this release is introducing support for SCP (`#137`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#137`_
      - enhancement
      - high
      - Support for SCP
      - alpha 1
    * - `#284`_
      - bug
      - medium
      - Index handling issue for multiple connections 
      - alpha 1
    * - `#299`_
      - enhancement
      - medium
      - Add posibility to restrict binding to specific interface when using tunneling
      - rc 1
    * - `#297`_
      - bug
      - low
      - `Put Directory` issue with Windows path destination
      - rc 1
    * - `#283`_
      - enhancement
      - low
      - SSHLibrary should understand ssh hostnames form .ssh/config
      - rc 1

Altogether 5 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.3.0>`__.

.. _#137: https://github.com/robotframework/SSHLibrary/issues/137
.. _#284: https://github.com/robotframework/SSHLibrary/issues/284
.. _#299: https://github.com/robotframework/SSHLibrary/issues/299
.. _#297: https://github.com/robotframework/SSHLibrary/issues/297
.. _#283: https://github.com/robotframework/SSHLibrary/issues/283
