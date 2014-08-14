========================
InstallationInstructions
========================

This guide explains how to install Robot Framework SSHLibrary on Linux and Windows. The Linux parts likely work for other Unix-like operating systems (like OS X) as well.

The guide is divided as following:
.. contents::
  :local:
  :depth: 3

Using pip
---------


To use SSHLibrary with Python, a module named `Paramiko`__ is required, and additionally Paramiko requires `PyCrypto`__ module as its dependency.


Depending on the `installation approaches`__ discussed further below, Paramiko and PyCrypto may be installed automatically by SSHLibrary.

If not automatically installed, you may use your distribution's package manager. For example on Debian variants, running `sudo apt-get install python-paramiko` should install them.

Alternatively, you can always install them using the source distributions from PyPI:
  * PyCrypto: https://pypi.python.org/pypi/pycrypto
  * Paramiko: https://pypi.python.org/pypi/paramiko


On Windows, you should always install PyCrypto using the `binary installer`__ *before* installing Paramiko. This is because installing PyCrypto automatically would require a C compiler. Make sure you pick the correct Paramiko installer depending on your Python version and CPU architecture.

Like on Linux, Paramiko may be installed automatically by SSHLibrary, but you can also install it yourself using the `source distribution`__.


To use SSHLibrary with Jython, Trilead SSH library is required.

Regardless of the operating system, you need to download `Trilead SSH JAR distribution`__ and append its path to your CLASSPATH.



The easiest way to install SSHLibrary is using `pip package manager`__.

If you do not want to install pip, or are using Jython which does not support it, you can always install SSHLibrary using the source distribution.

If you have `setuptools`__ (or its fork `distribute`__) installed,  `the dependencies`__ should be installed automatically by both of the following approaches. However, on Windows you still need to install PyCrypto binaries first.


With `pip`, all you need to do is run the following command:
::

    pip install robotframework-sshlibrary


Verifying the installation
==========================

  #. Download the source tar.gz at https://pypi.python.org/pypi/robotframework-sshlibrary.
  #. Extract the package to a temporary location.
  #. Open a terminal / command prompt.
  #. `cd` to the extracted directory.
  #. Run `python setup.py install` or `jython setup.py install`, depending on which interpreter you are using.



To test that the installation of SSHLibrary and its dependencies was successful, run in a terminal / command prompt:

::

        python -c "import SSHLibrary"

or
::

        jython -c "import SSHLibrary"


If you get no error messages, SSHLibrary is installed correctly.

__ http://www.lag.net/paramiko
__ http://www.pycrypto.org
__ `Installation`_
__ http://www.voidspace.org.uk/python/modules.shtml#pycrypto
__ https://pypi.python.org/pypi/paramiko
__ http://search.maven.org/remotecontent?filepath=com/trilead/trilead-ssh2/1.0.0-build217/trilead-ssh2-1.0.0-build217.jar
__ http://www.pip-installer.org
__ http://pythonhosted.org/setuptools/
__ http://pythonhosted.org/distribute/
__ `Dependencies`_
