""" simple_python_file

    what people are saying about this file:
      pep8:
        codebox/simple_python_file.py:5:1: E302 expected 2 blank lines, found 1
      pyflakes:
        codebox/simple_python_file.py:16: undefined name 'os'
        codebox/simple_python_file.py:19: local variable 'a' is assigned to but never used
        codebox/simple_python_file.py:26: local variable 'x' is assigned to but never used
        codebox/simple_python_file.py:27: local variable 'x' is assigned to but never used

"""



class Klass(object):
    """ docstring """
    def __init__(self):
        return

    def method(self):
        return os.path.exists

def f():
    a = 1
    return 32
def g():
    return 4


def a():
    def b(): x='in b()'
    x='in a()'; b()
f(); a()

from kinbaku.snoopy import snoop
f = snoop(f)
f() # calling f a second time
print 'fin: executing a simple python file'
