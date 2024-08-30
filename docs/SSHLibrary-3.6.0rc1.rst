====================================
SSHLibrary 3.6.0 Release Candidate 1
====================================


.. default-role:: code


SSHLibrary_ is a `Robot Framework`_ test library for SSH and SFTP.
SSHLibrary 3.6.0rc1 is a new release with several enhancements and bug fixes.
All issues targeted for SSHLibrary v3.6.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-sshlibrary

to install the latest release or use

::

   pip install robotframework-sshlibrary==3.6.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

SSHLibrary 3.6.0rc1 was released on Wednesday December 9, 2020.

.. _Robot Framework: http://robotframework.org
.. _SSHLibrary: https://github.com/MarketSquare/SSHLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-sshlibrary
.. _issue tracker: https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.5.0


.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Big thank you to the following contributors from the community:

- @kallepokki for Support logins without authentication (`#370`_, rc 1)
- @mika-b for Extend jump host functionality to password logins (`#369`_, rc 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#354`_
      - enhancement
      - medium
      - Presence of SSH config file breaks plain host connections
      - rc 1
    * - `#357`_
      - bug
      - high
      - Execute command with sudo appends incorrect newline to output
      - rc 1
    * - `#358`_
      - enhancement
      - medium
      - add support to preserve original timestamps (scp -p)
      - rc 1
    * - `#369`_
      - enhancement
      - medium
      - Extend jump host functionality to password logins
      - rc 1
    * - `#370`_
      - enhancement
      - medium
      - Support logins without authentication
      - rc 1

Altogether 5 issues. View on the `issue tracker <https://github.com/MarketSquare/SSHLibrary/issues?q=milestone%3Av3.6.0>`__.

.. _#354: https://github.com/MarketSquare/SSHLibrary/issues/354
.. _#357: https://github.com/MarketSquare/SSHLibrary/issues/357
.. _#358: https://github.com/MarketSquare/SSHLibrary/issues/358
.. _#369: https://github.com/MarketSquare/SSHLibrary/issues/369
.. _#370: https://github.com/MarketSquare/SSHLibrary/issues/370
