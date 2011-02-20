""" simple_python_file

    what people are saying about this file:
      pep8:
        codebox/simple_python_file.py:5:1: E302 expected 2 blank lines, found 1
"""
import os

def f():
    return 3

def g():
    return 4

class Klass(object):
    """ docstring """
    def __init__(self):
        return

    def method(self):
        return os.path.exists
