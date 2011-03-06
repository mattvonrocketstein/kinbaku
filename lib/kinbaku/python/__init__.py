""" kinbaku.python

     representation for various aspects of the python language itself.
"""
import os
from path import path

from kinbaku.python.comments import PythonComment as Comment
from kinbaku.python._module import PythonModule
from kinbaku.python.signatures import Signature

class Dotpath:
    """ """
    @staticmethod
    def scrape_dotpath_modules(fname):
        """ """
        lst = fname.split(os.path.sep)
        lst = [[element,
                path(os.path.sep.join(lst[:lst.index(element)+1]))] for element in lst if element]
        lst = [[element, partial] for element,partial in lst if partial and partial.isdir()]
        lst = [[element, partial, partial.files()] for element,partial in lst]
        lst = [[element, partial, [x.basename() for x in files]] for element,partial,files in lst ]
        lst = [[element, partial, files ] for element,partial,files in lst if '__init__.py' in files ]
        lst = [ PythonModule(name = element,
                             abspath = partial,
                             dotpath = '.'.join( [ x[0] for x in \
                                                lst[:lst.index([element,partial,files])+1]
                            ] )) \
                for element, partial, files in lst if '__init__.py' in files ]
        return lst

    @staticmethod
    def from_fname(fname):
        """ """
        for modyool in Dotpath.scrape_dotpath_modules(fname):
            if modyool.abspath == path(fname).abspath().parent:
              #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
              return Dotpath(modyool.dotpath) + Dotpath(fname.basename()[:-len(fname.ext)])

        return fname.replace('.py','').replace(os.path.sep, '.'),

    def __init__(self, dotpath):
        """ """
        self.dotpath = dotpath

    def __str__(self):
        """ """
        return '<Dotpath "' + self.dotpath + '">'

    def __add__(self, other):
        """ """
        return '.'.join([self.dotpath, other.dotpath])

def is_atom(arg):
    """ an argument is an atom iff it is
        equal to the evaluation of it's
        representation """
    try:
        return arg==eval(repr(arg))
    except SyntaxError:
        return False
