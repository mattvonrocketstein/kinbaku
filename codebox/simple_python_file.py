""" simple_python_file

    what people are saying about this file:
      pep8:
        codebox/simple_python_file.py:5:1: E302 expected 2 blank lines, found 1
      pyflakes:
        codebox/simple_python_file.py:16: undefined name 'os'
        codebox/simple_python_file.py:19: local variable 'a' is assigned to but never used
        codebox/simple_python_file.py:26: local variable 'x' is assigned to but never used
        codebox/simple_python_file.py:27: local variable 'x' is assigned to but never used
      pylint:
        C:  8: Line too long (90/80)
        C:  9: Line too long (90/80)
        C: 10: Line too long (90/80)
        C: 20:Klass.method: Missing docstring
        R: 20:Klass.method: Method could be a function
        R: 15:Klass: Too few public methods (1/2)
        W: 24:function_f: Redefining name 'a' from outer scope (line 31)
        C: 23:function_f: Missing docstring
        C: 24:function_f: Invalid name "a" (should match [a-z_][a-z0-9_]{2,30}$)
        W: 24:function_f: Unused variable 'a'
        C: 27:function_g: Missing docstring
        C: 31:a: Invalid name "a" (should match [a-z_][a-z0-9_]{2,30}$)
        C: 31:a: Missing docstring
        C: 32:a.b: Invalid name "b" (should match [a-z_][a-z0-9_]{2,30}$)
        C: 32:a.b: Missing docstring
        C: 32:a.b: More than one statement on a single line
        C: 32:a.b: Invalid name "x" (should match [a-z_][a-z0-9_]{2,30}$)
        W: 32:a.b: Unused variable 'x'
        C: 33:a: Operator not preceded by a space
            x='in a()'; b()
             ^
        C: 33:a: Invalid name "x" (should match [a-z_][a-z0-9_]{2,30}$)
        C: 33:a: More than one statement on a single line
        W: 33:a: Unused variable 'x'
        C: 34: More than one statement on a single line
        C: 37: Invalid name "function_f" (should match (([A-Z_][A-Z0-9_]*)|(__.*__))$)

"""
import os

class Klass(object):
    """ docstring """
    def __init__(self):
        return

    def method(self):
        return os.path.exists

def function_f(arg1, karg1='defaultkarg'):
    a = 1
    return 32

def function_g():
    return 4


def a():
    def b(): x='in b()'
    x='in a()'; b()
function_f("third"); a()

from kinbaku.snoopy import snoop
function_f(dict(a='b'),karg1='33')  # calling f a second time
function_g()             # calling g the first time
print 'fin: executing a simple python file'
