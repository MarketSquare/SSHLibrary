====================================
SSHLibrary 3.0.0 Release Candidate 1
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.0.0 release candidate 1 is a new release with Python 3 support and
few smaller fixes and enhancements.
All issues targeted for SSHLibrary v3.0.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.0.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.0.0rc1 was released on Tuesday April 24, 2018.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.0.0


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The main new feature in SSHLibrary 3.0 is the support for Python 3 (`#219`_).

Another important feature is the possibility to use sudo to execute and start commands (`#189`_). 

Backwards incompatible changes
==============================

New arguments were added to `Login with Public Key` keyword and `delay` must be provided as a named argument (`#146`_).

Acknowledgements
================

Thanks to `@rainmanwy <https://github.com/rainmanwy>`_ for the Python 3
pull request (`#207`_) and also others who provided earlier PRs related
to it.

Big thanks also to `Mihai Pârvu <https://github.com/mihaiparvu>`_,
`Oana Brinzan <https://github.com/oanab11>`_ and
`Andreea Kovacs <https://github.com/andreeakovacs>`_ for their work and
especially for promising to work as SSHLibrary maintainers!

.. _#207: https://github.com/MarketSquare/SSHLibrary/pull/207


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
    * - `#189`_
      - enhancement
      - high
      - sudo for  "Execute Command" and "Start Command" 
      - rc 1
    * - `#182`_
      - bug
      - medium
      - 'Put Directory' command doesn't upload correctly the files with ':' in the name.
      - alpha 1
    * - `#146`_
      - enhancement
      - medium
      - Login using agent forwarding
      - rc 1
    * - `#199`_
      - enhancement
      - medium
      - Support regexp for connection prompt
      - alpha 1
    * - `#201`_
      - enhancement
      - medium
      - Add support for Travis CI
      - alpha 1
    * - `#132`_
      - enhancement
      - low
      - Capture the pre login banner
      - rc 1

Altogether 7 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.0.0>`__.

.. _#219: https://github.com/MarketSquare/SSHLibrary/issues/219
.. _#189: https://github.com/MarketSquare/SSHLibrary/issues/189
.. _#182: https://github.com/MarketSquare/SSHLibrary/issues/182
.. _#146: https://github.com/MarketSquare/SSHLibrary/issues/146
.. _#199: https://github.com/MarketSquare/SSHLibrary/issues/199
.. _#201: https://github.com/MarketSquare/SSHLibrary/issues/201
.. _#132: https://github.com/MarketSquare/SSHLibrary/issues/132
