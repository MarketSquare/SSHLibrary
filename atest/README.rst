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

    sudo cp ~/testkey/.ssh/id_rsa <path_to_sshlibrary>/atest/testdata/keyfiles/

Running the acceptance tests
============================

Tests also require robotstatuschecker:

::

    pip install robotstatuschecker
 
Tests are ran using Bash script `atest/run_atests.sh`. The script prints help when ran without parameters.