================
SSHLibrary 3.2.1
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.2.1 is a bug-fix release.
All issues targeted for SSHLibrary v3.2.1 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.2.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.2.1 was released on Thursday November 8, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.2.1


.. contents::
   :depth: 2
   :local:

Most important update
=====================

- Removing connections from connection list breaks switch_connection when followed by a close_connection (`#279`_)

Backwards incompatible changes
==============================

- Get Directory now downloads also the folder not only its content (`#270`_)

Acknowledgements
================

Thank you @jluhrsen for reporting the issue and providing a fix:

- Removing connections from connection list breaks switch_connection when followed by a close_connection (`#279`_)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#279`_
      - bug
      - high
      - Removing connections from connection list breaks switch_connection when followed by a close_connection
    * - `#270`_
      - bug
      - medium
      - Get Directory downloads only the content of the folder
    * - `#248`_
      - bug
      - low
      - SSHLibrary: not possible to change (width/height) of existing session

Altogether 3 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.2.1>`__.

.. _#279: https://github.com/MarketSquare/SSHLibrary/issues/279
.. _#270: https://github.com/MarketSquare/SSHLibrary/issues/270
.. _#248: https://github.com/MarketSquare/SSHLibrary/issues/248
