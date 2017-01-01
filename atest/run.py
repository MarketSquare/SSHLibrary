#!/usr/bin/env python

"""usage: (python|jython) atest/run.py <test_suite_path>"

    Examples:
    Running all the tests with Pybot:
    python atest/run.py atest

    Pybot results are found in path 'atest/results/python/'

    Running all the tests with Jybot:
    jython atest/run.py atest

    Jybot results are found in path 'atest/results/jython/
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

sys.path.append(join(CURDIR, '..', 'src'))

COMMON_OPTS = ('--log', 'NONE', '--report', 'NONE')

def atests(*opts):
    if os.name == 'java':
        jython(*opts)
        process_output(join(OUTPUT_JYTHON, 'output.xml'))
        return rebot(join(OUTPUT_JYTHON, 'output.xml'), outputdir=OUTPUT_JYTHON)
    elif os.name == 'nt':
        os_includes = ('--include', 'windows')
    else:
        os_includes = ('--exclude', 'windows')
    python(*(os_includes+opts))
    process_output(join(OUTPUT_PYTHON, 'output.xml'))
    return rebot(join(OUTPUT_PYTHON, 'output.xml'), outputdir=OUTPUT_PYTHON)

def python(*opts):
    try:
        run_cli(['--outputdir', OUTPUT_PYTHON,
                '--include', 'pybot']
                + list(COMMON_OPTS + opts))
    except SystemExit:
        pass

def jython(*opts):
    try:
        run_cli(['--outputdir', OUTPUT_JYTHON,
                '--pythonpath', JAR_PATH,
                '--include', 'jybot']
                + list(COMMON_OPTS + opts))
    except SystemExit:
        pass

if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print(__doc__)
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    print "\nAfter status check there were %s failures." % rc
    sys.exit(rc)