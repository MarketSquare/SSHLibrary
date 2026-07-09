================================================
  How to run SSHLibrary's own acceptance tests
================================================

This guide tells how to run the acceptance tests of SSHLibrary. Acceptance tests basically require an SSH server (`OpenSSH <http://www.openssh.org>`__ recommended) installed and running and two user accounts to be created for the tests.

Because SSHLibrary is primary used on Linux, tests should be ran at least on it. If developing on OS X or Windows, setting up a virtual machine with Linux and SSHLibrary installed is the recommended approach.

Setup IDE
=========

Use ``robotframework-tidy`` to format the test files. It can be installed with pip: ``pip install robotframework-tidy``. If you do not format test cases according to robotidy, the PR check will fail automatically.

Setup on Linux
==============

- Install OpenSSH server (using apt-get on Debian variants):

::

    sudo apt-get install openssh-server

- Create a new user ``test``:

::

    sudo useradd test -m -s /bin/bash

- With password ``test``:

::

    sudo passwd test
    (input `test` as the new password)

- Add ``test`` user to the sudoers list::

    sudo adduser test sudo
    (input `test` as UNIX password)

- Log in as ``test``

::

    sudo su test

- Set prompt in ``.bashrc``

::

    export PS1='\u@\h \W \$ '

- exit

- Create a new user ``test-nopasswd``:

::

	sudo useradd --create-home --shell /bin/bash test-nopasswd

- Delete it's password

::

	sudo passwd --delete test-nopasswd

- Create a new user ``testkey``:

::

    sudo useradd -m testkey -s /bin/bash

- Log in as ``testkey``:

::

    sudo su testkey

- Set prompt in `.bashrc`

::

    export PS1='\u@\h \W \$ '

- Generate a new SSH key pair:

::

    ssh-keygen -t rsa
    (input empty password)

- Add the public key to user's authorized keys:

::

    cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys

- Make the key known to the ssh agent:

::

    ssh-add ~/.ssh/id_rsa

- Log out, back to your normal user account:

::

    exit

- Finally, copy ``id_rsa`` of user ``testkey`` into directory ``atest/testdata/keyfiles``:

::

    sudo cp ~testkey/.ssh/id_rsa <path_to_sshlibrary>/atest/testdata/keyfiles/

- Change the rights for that file so that you can read it.

Additional OpenSSH configuration
################################

- Open sshd configuration file ``/etc/ssh/sshd_config`` using a text editor

- Add/edit the following lines:

::
    PermitEmptyPasswords yes
    Banner /etc/ssh/sshd-banner # for testing pre-login banner
    Subsystem subsys echo "Subsystem invoked." # for testing invoke_subsystem

- Save file and restart the ssh server:

::

    sudo /etc/init.d/ssh restart

- Create a new file ``/etc/ssh/sshd-banner`` containing:

::

    Testing pre-login banner


- Add test_hostname, testkey_hostname, test_proxy_hostname and test_user_hostname in ``~/.ssh/config``

::

    echo $'Host test_hostname\n    Hostname localhost\n    User test\n    Port 22\n' >> ~/.ssh/config

::

    echo $'Host testkey_hostname\n    Hostname localhost\n    User testkey\n    Port 22\n    IdentityFile <path_to_sshlibrary>/atest/testdata/keyfiles/id_rsa\n' >> ~/.ssh/config

::

    echo $'Host test_proxy_hostname\n    Hostname localhost\n    User test\n    Port 22\n    ProxyCommand ssh -W %h:%p testkey_hostname\n' >> ~/.ssh/config

::

    echo $'Host test_user_hostname\n    Hostname localhost\n    User nonexisting\n    Port 22\n' >> ~/.ssh/config


Setup for Docker
================
First go into the ``docker`` folder and build a SSHLibrary image that will be based on your repository:

::

    sudo docker build -t sshlibrary --build-arg repository=<link_to_desired_sshlibrary_repository> .


Go to the ``docker-compose.yml`` file and change the branch name so that the chosen git branch will be selected:

::

    command: /bin/bash -c "service ssh start && && eval $$(ssh-agent -s) && ssh-add /home/testkey/.ssh/id_rsa &&
    cd SSHLibrary && git checkout <branch_name> && git pull origin <branch_name> && python3 atest/run.py ."

Save the changes and create a folder ``results`` in the ``docker`` folder, that will be used by
``docker-compose`` to get from the container the test reports:

::

    mkdir results


Run the docker-compose file:

::

    sudo docker-compose up -d


After running the latest command some time will be required for the acceptance tests to be executed. The results
files can be found in the ``/docker/results/python`` folder.

To follow the test execution in real time use the command:

::

    sudo docker logs <container_id> --follow

Setup in Windows
================
The acceptance tests can also be run on Windows. The recommended way is to use the WSL (Windows Subsystem for Linux) available in Windows 10.

Running the acceptance tests
============================

Tests also require ``robotstatuschecker``:

::

    pip install robotstatuschecker

Tests are ran using Bash script ``python atest/run.py``. The script prints help when ran without parameters.

In order to run the tests with IPv6, the ``::1`` must be used as host variable when running ``atest/run.py`` script::

    python atest/run.py --variable=HOST:::1 atest


