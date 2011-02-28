""" kinbaku.types
"""
import os
import compiler

from kinbaku.report import console, report
from kinbaku.python.signatures import Signature
from kinbaku.python import Comment
from kinbaku.python import is_atom

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

class KinbakuFile(object):
    """ Convenience for wrapping files
    """
    def __init__(self,fname=None,fhandle=None):
        self.fname = fname
        self._fhandle=fhandle

    @property
    def fhandle(self):
        return self._fhandle or open(self.fname,'r')

    @property
    def contents(self):
        return self.fhandle.read()

    @property
    def ast(self):
        try:
            return compiler.parse(self.contents)
        except IOError:
            print console.red("IOError: {f}".format(f=str(self.fname)))
            return

    def parse(self): return self.ast

    def run_cvg(self):
        """ """
        fhandle     = StringIO.StringIO("")
        report_args = dict( ignore_errors = False, omit = '',
                            include = '', morfs = [],
                            file = fhandle, )

        cscript = CoverageScript()
        status  = cscript.command_line(['run', self.fname])
        if status == 0:
            cscript.coverage.report(show_missing=True, **report_args)
            fhandle.seek(0);
            results = fhandle.read()
            return results
        else:
            raise Exception,['not sure what to do with cvg status:',status]
