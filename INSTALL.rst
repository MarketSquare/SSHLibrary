=============================
  Installation instructions
=============================

This guide explains how to install Robot Framework SSHLibrary on Linux
and Windows. The Linux parts likely work also on OSX and other
UNIX-like operating systems.

The guide is divided as following:

.. contents::
  :local:
  :depth: 2

Installing dependencies
=======================

On Python
---------

To use SSHLibrary with Python, you will need to have `paramiko
<http://paramiko.org>`__ SSH module and its dependency `PyCrypto
<http://pycrypto.org>`__ installed. How to install them depends on
are you on Linux or Windows.

On Linux
~~~~~~~~

If you are `using pip`_ to install SSHLibrary itself, you should get both
Paramiko and PyCrypto installed automatically.

Alternatively you can use your distribution's package manager. For
example, on Debian based systems ``sudo apt-get install
python-paramiko`` should install both Paramiko and PyCrypto.

The last alternative is downloading and installing source distributions:

- Paramiko: https://pypi.python.org/pypi/paramiko
- PyCrypto: https://pypi.python.org/pypi/pycrypto

On Windows
~~~~~~~~~~

On Windows, you should always install PyCrypto using the `binary
installer <http://www.voidspace.org.uk/python/modules.shtml#pycrypto>`__
*before* installing Paramiko or SSHLibrary. This is because installing
PyCrypto automatically would require a C compiler. Make sure you pick
the correct Paramiko installer depending on your Python version and
CPU architecture.

Like `on Linux`_, Paramiko can be installed automatically if `using
pip`_ to install SSHLibrary itself. Alternatively you can download and
install the `source distribution <https://pypi.python.org/pypi/paramiko>`__.

On Jython
---------

To use SSHLibrary with Jython, Trilead SSH library is required.

Regardless of the operating system, you need to download `Trilead SSH
JAR distribution`__ and add it to CLASSPATH.

__ http://search.maven.org/remotecontent?filepath=com/trilead/trilead-ssh2/1.0.0-build217/trilead-ssh2-1.0.0-build217.jar

Installing SSHLibrary
=====================

Using pip
---------

The easiest way to install SSHLibrary is using `pip package manager
<http://pip-installer.org>`__::

    pip install robotframework-sshlibrary

A benefit of pip is that it installs dependencies automatically. Notice that
`on Windows`_ you should still install PyCrypto manually first.

Using source distribution
-------------------------

If you do not want or cannot install pip, you can always install
SSHLibrary using the source distribution:

1. Download the source distribution from
   https://pypi.python.org/pypi/robotframework-sshlibrary.
2. Extract the package to a temporary location.
3. Open command prompt and navigate to the extracted directory.
4. Run one of the following depending are you using Python or Jython::

     python setup.py install
     jython setup.py install

Verifying installation
======================

To test that installing SSHLibrary and its dependencies was successful,
run one of the commands depending on the interpreter you use::

    python -c "import SSHLibrary"
    jython -c "import SSHLibrary"

If you get no error messages, SSHLibrary is installed correctly.
