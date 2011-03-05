""" kinbaku.python

     representation for various aspects of the python language itself.
"""

from kinbaku.python.comments import PythonComment as Comment
from kinbaku.python._module import PythonModule
from kinbaku.python.signatures import Signature

def is_atom(arg):
    """ an argument is an atom iff it is
        equal to the evaluation of it's
        representation """
    try:
        return arg==eval(repr(arg))
    except SyntaxError:
        return False
