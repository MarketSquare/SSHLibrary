================================================
  How to run SSHLibrary's own acceptance tests
================================================

This guide tells how to run the acceptance tests of SSHLibrary. Acceptance tests basically require an SSH server (`OpenSSH <http://www.openssh.org>`__ recommended) installed and running and two user accounts to be created for the tests.

Because SSHLibrary is primary used on Linux, tests should be ran at least on it. If developing on OS X or Windows, setting up a virtual machine with Linux and SSHLibrary installed is the recommended approach.

Setup on Linux
==============

- Install `openSSH` server (using apt-get on Debian variants):

::

    sudo apt-get install openssh-server

- Create a new user `test`:

::

    sudo useradd test -m -s /bin/bash

- With password `test`:

::

    sudo passwd test
    (input `test` as the new password)

- Add `test` user to the sudoers list::

    sudo adduser test sudo
    (input `test` as UNIX password)

- Log in as `test`

::

    sudo su test

- Set prompt in .bashrc

::

    export PS1='\u@\h \W \$ '

- exit

- Create a new user `testkey`:

::

    sudo useradd -m testkey -s /bin/bash

- Log in as `testkey`:

::

    sudo su testkey

- Set prompt in .bashrc

::

    export PS1='\u@\h \W \$ '

- Generate a new SSH key pair:

::

    ssh-keygen -t rsa
    (input empty password)

- Add the public key to user's authorized keys:

::

    cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys

- Log out, back to your normal user account:

::

    exit

- Finally, copy `id_rsa` of user `testkey` into directory `atest/testdata/keyfiles`:

::

    sudo cp ~testkey/.ssh/id_rsa <path_to_sshlibrary>/atest/testdata/keyfiles/

- Change the rights for that file so that you can read it.
- Create your login banner file /etc/ssh/sshd-banner and append text:

::

    Testing pre-login banner

- Open sshd configuration file /etc/ssh/sshd_config using a text editor

- Add/edit the following line:

::

    Banner /etc/ssh/sshd-banner

- Save file and restart the ssh server:

::

    sudo /etc/init.d/ssh restart

- Add test_hostname in ~/.ssh/config

::

    echo $'Host test_hostname\n    Hostname localhost\n' >> ~/.ssh/config


Setup in Windows
================
The acceptance tests can also be run on windows against a ssh server running on Cygwin.

You will need to install Cygwin with SSH server. Then add users test and testkey and follow the same steps as in linux to setup their bash accounts on Cygwin. After that you can execute the acceptance tests on Windows.

The tests assume that Cygwin is installed to c:/cygwin64. If the installation irectory is different, it can be overridden with commadnline option `--variable CYGWIN_HOME:<the real path>`

Running the acceptance tests
============================

Tests also require robotstatuschecker:

::

    pip install robotstatuschecker

Tests are ran using Bash script `python atest/run.py`. The script prints help when ran without parameters.

In order to run the tests with IPv6, the ``::1`` must be used as host variable when running ``atest/run.py`` script::

    python atest/run.py --variable=HOST:::1 atest
