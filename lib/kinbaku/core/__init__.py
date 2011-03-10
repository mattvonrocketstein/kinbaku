""" kinbaku.core
"""
import compiler
from StringIO import StringIO

from path import path
from pygenie.cc import measure_complexity, PrettyPrinter

import os
from kinbaku.util import is_python

def dir2files(dir,python=False):
    """ TODO: does path.path work recursively for files() ? """
    if not dir or not os.path.exists(dir):
            return []
    pth_root = path(dir)
    if not pth_root.isdir():
        all_files = [pth_root]
    else:
        all_files = pth_root.files()
    if python:
        out = filter(is_python, all_files)
    else:
        out = all_files
    return out


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
        from kinbaku._pygenie import gettype, getpath
        from kinbaku.python import Dotpath
        if not self.contents:
            return
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
        from coverage.misc import ExceptionDuringRun
        from kinbaku._coverage import CoverageScript
        fhandle     = StringIO("")
        cscript     = CoverageScript()
        report_args = dict( ignore_errors = False,
                            #omit = '',
                            #include = '',
                            morfs = [],
                            file = fhandle, )


        try:
            status  = cscript.command_line(['run', self.fname])
        except IndexError: #empty file?
            return None
        except SyntaxError:
            return None
        except ExceptionDuringRun,e: # bad file.  probably would be caught by pyflakes
            return None
        if status == 0:
            cscript.coverage.report(show_missing=True, **report_args)
            fhandle.seek(0);
            results = fhandle.read()
            return results
        else:
            raise Exception,['not sure what to do with cvg status:',status]
    cvg=run_cvg

    @property
    def coverage(self):
        cvg = self.cvg()
        if not cvg: return None
        result_line = [ x.split() for x in cvg.split('\n') if x ][-1]
        fname  = result_line[0]
        statements  = result_line[1]
        executed  = result_line[2]
        covered  = result_line[3]

        if fname=='TOTAL': # should not happen
            return

        from kinbaku._coverage import FileCoverage
        fpath_cvg = FileCoverage(fname=fname+'.py',
                                 statements=statements,
                                 cover=int(covered[:-1]),
                                 )
        return fpath_cvg

    @property
    def percent_covered(self):
        """ for sorting -- numerical (int) percent from the coverage object """
        out = self.coverage
        return out and out.cover
