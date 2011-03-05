""" kinbaku.types
"""
import os
import compiler

from kinbaku.report import console, report
#from kinbaku.python.signatures import Signature
#from kinbaku.python import Comment
#from kinbaku.python import is_atom

class UnusableCodeError(ValueError): pass
class BadDotPath(ValueError):        pass

class Bag(object):
    """ a bag of named stuff """
    def __repr__(self): return str(self)
    def __init__(self, **kargs):
        """ """
        [ setattr(self, k, v) for k,v in kargs.items() ]

    def __str__(self):
        return self.__class__.__name__ +"\n  "+ str(self.__dict__)


class Match(object):
    """ generic representation of a match """
    def __str__(self):
        return 'Match_'+str(self.__dict__)

    __repr__=__str__

    def __init__(self, **kargs):
        for k,v in kargs.items(): setattr(self,k,v)

