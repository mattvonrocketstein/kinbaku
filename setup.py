#!/usr/bin/env python
""" setup.py for kinbaku
"""

import os, sys, subprocess
import errno, shutil

from setuptools import setup, find_packages
from optparse import OptionParser

BASEDIR = os.path.dirname(os.path.realpath(__file__))


setup(
    name         ='kinbaku',
    version      = '.1',
    description  = 'use cases for rope',

    author       = 'mattvonrocketstein, in the gmails',
    url          = 'one of these days',

    package_dir  = {'': 'lib'},
    packages     = find_packages('lib'),
    entry_points = {
        'console_scripts': [
            'kinbaku = kinbaku.bin.kbk:entry',
         ],
    },
)
