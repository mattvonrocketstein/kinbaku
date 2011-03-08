""" kinbaku.core
"""
import StringIO
import compiler
from StringIO import StringIO

from path import path
from pygenie.cc import measure_complexity, PrettyPrinter

def gettype(x):
    """ """
    if x=='X': return 'file'
    if x=='M': return 'method'
    if x=='C': return 'class'
    if x=='F': return 'function'
    return x

def getpath(_type,dotpath):
    """ """
    if _type=='X': return path(dotpath).abspath()
    return dotpath #Dotpath(dotpath)

class KinbakuFile(object):
    """ Convenience for wrapping files
    """
    def __init__(self,fname=None,fhandle=None):
        self.fname = fname
        self._fhandle=fhandle

    @property
    def fhandle(self):
        """ """
        return self._fhandle or open(self.fname,'r')

    @property
    def contents(self):
        """ """
        x = self.fhandle.read()
        if x:
            return x
        self.fh
    @property
    def ast(self):
        """ """
        if not self.contents:
            return
        try:
            return compiler.parse(self.contents)
        except SyntaxError:
            raise SyntaxError,"Reading file:\n"+self.contents
        except IOError:
            print console.red("IOError: {f}".format(f=str(self.fname)))
            return

    def parse(self): return self.ast

    def complexity(self):
        """ returns cyclomatic complexity statistics
            in the following format:

            [ ('X', 'some/path/name.py', complexity_score),
              ('C', 'SomeClass',         complexity_score),
              ('M', 'SomeClass.__str__', complexity_score), ]
        """
        from kinbaku.python import Dotpath

        try:
            stats = measure_complexity(self.contents, self.fname)
        except SyntaxError:
            return None
        out   = PrettyPrinter(StringIO()).flatten_stats(stats)
        out   = [ [ gettype(_type),
                    getpath(_type,dotpath),
                    score ] for _type, dotpath, score in out ]
        return out

    def run_cvg(self):
        """ """
        from kinbaku._coverage import CoverageScript
        fhandle     = StringIO.StringIO("")
        report_args = dict( ignore_errors = False,
                            #omit = '',
                            #include = '',
                            morfs = [],
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
