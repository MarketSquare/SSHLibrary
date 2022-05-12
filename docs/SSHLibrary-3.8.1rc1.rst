===================
SSHLibrary 3.8.1rc1
===================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.8.1rc1 is a new release with
**UPDATE** enhancements and bug fixes.
All issues targeted for SSHLibrary v3.8.1 can be found from
the `issue tracker`_.

**REMOVE the previous note about all issues in the tracker with final
releases or otherwise if release notes contain all issues.**

**ADD more intro stuff if needed...**

**REMOVE ``--pre`` from the next command with final releases.**

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.8.1rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.8.1rc1 was released on Thursday May 12, 2022.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.8.1


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

**EXPLAIN** or remove these.

- SSHLibrary not working with RF`#5`_.0a1 (`#401`_, rc 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#401`_
      - enhancement
      - high
      - SSHLibrary not working with RF`#5`_.0a1
      - rc 1
    * - `#374`_
      - bug
      - medium
      - Library raises Authentication failure, but host accepted it
      - rc 1
    * - `#412`_
      - bug
      - low
      - SSH.Execute Command Giving Warning while Inputting Password ${stderr} [sudo] password for supervisor: Sorry, try again
      - rc 1

Altogether 3 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.8.1>`__.

.. _#401: https://github.com/robotframework/SSHLibrary/issues/401
.. _#374: https://github.com/robotframework/SSHLibrary/issues/374
.. _#412: https://github.com/robotframework/SSHLibrary/issues/412
