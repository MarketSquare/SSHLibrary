This directory contains simple example test cases using SSHLibrary for
Robot Framework.

To run these tests, install SSHLibrary and execute `pybot executing_commands.txt`

By default the connection is made using parameters read from the resource
file. They can be changed by using command line options, for example:

pybot -v host:somehost -v user:somebody -v password:secret executing_commands.txt
