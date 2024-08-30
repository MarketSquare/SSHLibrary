================
SSHLibrary 3.8.0
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.8.0 is a new release with several enhancements and bug fixes.
All issues targeted for SSHLibrary v3.8.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.8.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.8.0 was released on Thursday November 18, 2021.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.8.0


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
    * - `#388`_
      - bug
      - medium
      - Get File scp=ALL depends on nonstandard utility
    * - `#104`_
      - enhancement
      - medium
      - File Should Exist not allowing GLOB
    * - `#350`_
      - enhancement
      - low
      - execute command with sudo has a potential password exposure

Altogether 3 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.8.0>`__.

.. _#388: https://github.com/MarketSquare/SSHLibrary/issues/388
.. _#104: https://github.com/MarketSquare/SSHLibrary/issues/104
.. _#350: https://github.com/MarketSquare/SSHLibrary/issues/350
