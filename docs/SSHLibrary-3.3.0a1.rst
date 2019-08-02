========================
SSHLibrary 3.3.0 alpha 1
========================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.3.0a1 is a new release with SCP support and bug fixes.
All issues targeted for SSHLibrary v3.3.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.3.0a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.3.0a1 was released on Thursday January 31, 2019.

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
      - Bug at SSHConnectionCache SSHLibrary version 3.2.1
      - alpha 1

Altogether 2 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.3.0>`__.

.. _#137: https://github.com/robotframework/SSHLibrary/issues/137
.. _#284: https://github.com/robotframework/SSHLibrary/issues/284
