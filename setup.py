#!/usr/bin/env python
""" setup.py for kinbaku

      this pattern stolen from pygments setup.py
"""

import os
from setuptools import setup, find_packages
os.chdir(os.path.abspath(os.path.split(__file__)[0]))

try:
    from setuptools import setup, find_packages
    have_setuptools = True
except ImportError:
    from distutils.core import setup
    def find_packages():
        return [
            'kinbaku',
            'kinbaku.core',
            'kinbaku.plugin',
            'kinbaku.comments',
            'kinbaku.report',
            'kinbaku.run',
        ]
    have_setuptools = False
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

if have_setuptools:
    add_keywords = dict( entry_points = \
                         { 'console_scripts': \
                           ['kinbaku = kinbaku.bin.kbk:entry', \
                            'kbk-comments = kinbaku.bin.kbk:comments', \
                            'kbk-run = kinbaku.bin.kbk:run', \
                            'kbk-scope = kinbaku.bin.kbk:scope'], \
                         }, )
else:
    add_keywords = dict( scripts = ['kinbaku'], )

setup(
    name         ='kinbaku',
    version      = '.1',
    description  = 'use cases for rope',
    author       = 'mattvonrocketstein, in the gmails',
    url          = 'one of these days',
    license = 'BSD License',
    package_dir  = {'': 'lib'},
    packages     = find_packages('lib'),
    long_description = __doc__,
    keywords = 'tests tracing profiling ast',
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    cmdclass = {'build_py': build_py},
    **add_keywords
)
