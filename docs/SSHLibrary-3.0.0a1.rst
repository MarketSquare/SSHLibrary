==================
SSHLibrary 3.0.0a1
==================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.0.0a1 is a new release with
**UPDATE** enhancements and bug fixes.
All issues targeted for SSHLibrary v3.0.0 can be found from
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

   pip install robotframework-sshlibrary==3.0.0a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.0.0a1 was released on Thursday March 22, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/robotframework/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.0.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

**EXPLAIN** or remove these.

- Python 3 compatibility (`#219`_, alpha 1)

Acknowledgements
================

**UPDATE** based on AUTHORS.txt or similar.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#219`_
      - enhancement
      - critical
      - Python 3 compatibility
      - alpha 1
    * - `#182`_
      - bug
      - medium
      - 'Put Directory' command doesn't upload correctly the files with ':' in the name.
      - alpha 1
    * - `#199`_
      - enhancement
      - medium
      - support regexp for connection prompt
      - alpha 1
    * - `#201`_
      - enhancement
      - medium
      - Add support for Travis CI
      - alpha 1

Altogether 4 issues. View on the `issue tracker <https://github.com/robotframework/SSHLibrary/issues?q=milestone%3Av3.0.0>`__.

.. _#219: https://github.com/robotframework/SSHLibrary/issues/219
.. _#182: https://github.com/robotframework/SSHLibrary/issues/182
.. _#199: https://github.com/robotframework/SSHLibrary/issues/199
.. _#201: https://github.com/robotframework/SSHLibrary/issues/201
