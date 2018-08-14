================
SSHLibrary 3.1.1
================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.1.1 is a new minor release fixing a blocking issue
related to copying symbolic links, and a couple of bug fixes.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.1.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.1.1 was released on Tuesday August 14, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.1.1


List of fixed issues
====================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#131`_
      - bug
      - medium
      - Get File does not resolve symlinks
    * - `#255`_
      - bug
      - medium
      - Python tunneling issue with IPv6
    * - `#210`_
      - bug
      - low
      - Permissions are not properly set when copying a directory 

Altogether 3 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.1.1>`__.

.. _#131: https://github.com/robotframework/SSHLibrary/issues/131
.. _#255: https://github.com/robotframework/SSHLibrary/issues/255
.. _#210: https://github.com/robotframework/SSHLibrary/issues/210
