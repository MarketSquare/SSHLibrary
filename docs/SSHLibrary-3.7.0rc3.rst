====================================
SSHLibrary 3.7.0 Release Candidate 3
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.7.0rc3 is a new release that fixes longpath filenames
with Windows and improves performance when running Read Until
keywords.
All issues targeted for SSHLibrary v3.7.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.7.0rc3

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.7.0rc3 was released on Wednesday June 16, 2021.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.7.0


.. contents::
   :depth: 2
   :local:

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#129`_
      - bug
      - medium
      - Read gets in endless loop after encountering invalid encoding
      - rc 1
    * - `#376`_
      - bug
      - medium
      - Unable to use 'Put File' with wildcard and scp=ALL
      - rc 1
    * - `#368`_
      - enhancement
      - medium
      - Support main options from SSH config file
      - rc 1
    * - `#379`_
      - enhancement
      - medium
      - Reconnect Keyword
      - rc 1
    * - `#384`_
      - bug
      - low
      - Get Directory failing when getting sub folders from Linux to local Windows
      - rc 3

Altogether 5 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.7.0>`__.

.. _#129: https://github.com/robotframework/SSHLibrary/issues/129
.. _#376: https://github.com/robotframework/SSHLibrary/issues/376
.. _#368: https://github.com/robotframework/SSHLibrary/issues/368
.. _#379: https://github.com/robotframework/SSHLibrary/issues/379
.. _#384: https://github.com/robotframework/SSHLibrary/issues/384
