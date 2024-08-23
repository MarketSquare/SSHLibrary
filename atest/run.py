#!/usr/bin/env python

"""usage: (python) atest/run.py <test_suite_path>"

    Examples:
    Running all the tests with Robot:
    python atest/run.py atest

    Robot results are found in path 'atest/results/'

    Running tests with IPv6:
    Example:
        python atest/run.py --variable=HOST:::1 atest
"""
import sys
import os

from os.path import abspath, dirname, join
from robot import run_cli, rebot
from robotstatuschecker import process_output

CURDIR = dirname(abspath(__file__))
OUTPUT_ROOT = join(CURDIR, 'results')

sys.path.append(join(CURDIR, '..', 'src'))

COMMON_OPTS = ('--log', 'NONE', '--report', 'NONE')


def atests(*opts):
    os_includes = get_os_includes(os.name)
    python(*(os_includes + opts))
    process_output(join(OUTPUT_ROOT, 'output.xml'))
    return rebot(join(OUTPUT_ROOT, 'output.xml'), outputdir=OUTPUT_ROOT)


def get_os_includes(operating_system):
    if operating_system == 'nt':
        return '--exclude', 'linux'
    return '--exclude', 'windows'


def python(*opts):
    try:
        run_cli(['--outputdir', OUTPUT_ROOT]
                + list(COMMON_OPTS + opts))
    except SystemExit:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print(__doc__)
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    print(f"\nAfter status check there were {rc} failures.")
    sys.exit(rc)
