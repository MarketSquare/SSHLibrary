#!/usr/bin/env python

"""usage: (python|jython) atest/run.py <test_suite_path>"

    Examples:
    Running all the tests with Pybot:
    python atest/run.py atest

    Pybot results are found in path 'atest/results/python/'

    Running all the tests with Jybot:
    jython atest/run.py atest

    Jybot results are found in path 'atest/results/jython/

    Running tests with ipv6:
    Example:
        python atest/run.py ipv6 atest
        or
        jython atest/run.py ipv6 atest
"""
import sys
import os

from os.path import abspath, dirname, exists, join, normpath
from robot import run_cli, rebot
from robotstatuschecker import process_output


CURDIR = dirname(abspath(__file__))
OUTPUT_ROOT = join(CURDIR, 'results')
OUTPUT_PYTHON = join(OUTPUT_ROOT, 'python')
OUTPUT_JYTHON = join(OUTPUT_ROOT, 'jython')
JAR_PATH = join(CURDIR, '..', 'lib')
RESOURCES_PATH = join(CURDIR, 'resources')
VARIABLE_FILE_IPV4 = join(RESOURCES_PATH, 'getHostVariable.py:ipv4')
VARIABLE_FILE_IPV6 = join(RESOURCES_PATH, 'getHostVariable.py:ipv6')

sys.path.append(join(CURDIR, '..', 'src'))

COMMON_OPTS = ('--log', 'NONE', '--report', 'NONE')
variable_file = VARIABLE_FILE_IPV4

def atests(*opts):
    if os.name == 'java':
        os_includes = get_os_includes(os._name)
        jython(*(os_includes+opts))
        process_output(join(OUTPUT_JYTHON, 'output.xml'))
        return rebot(join(OUTPUT_JYTHON, 'output.xml'), outputdir=OUTPUT_JYTHON)
    else:
        os_includes = get_os_includes(os.name)
        python(*(os_includes+opts))
        process_output(join(OUTPUT_PYTHON, 'output.xml'))
        return rebot(join(OUTPUT_PYTHON, 'output.xml'), outputdir=OUTPUT_PYTHON)

def get_os_includes(operating_system):
    if operating_system == 'nt':
        return ('--include', 'windows',
                '--exclude', 'linux')
    return ('--include', 'linux',
            '--exclude', 'windows')

def python(*opts):
    try:
        run_cli(['--outputdir', OUTPUT_PYTHON,
             '--include', 'pybot',
             '--variablefile', variable_file]
            + list(COMMON_OPTS + opts))
    except SystemExit:
        pass

def jython(*opts):
    try:
        run_cli(['--outputdir', OUTPUT_JYTHON,
                '--pythonpath', JAR_PATH,
                '--include', 'jybot',
                '--variablefile', variable_file]
                + list(COMMON_OPTS + opts))
    except SystemExit:
        pass

if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print(__doc__)
        rc = 251
    elif 'ipv6' in sys.argv:
        variable_file = VARIABLE_FILE_IPV6
        rc = atests(*sys.argv[2:])
    else:
        rc = atests(*sys.argv[1:])
    print("\nAfter status check there were %s failures." % rc)
    sys.exit(rc)