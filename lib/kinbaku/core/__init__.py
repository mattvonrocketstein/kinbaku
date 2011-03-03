""" kinbaku.core
"""
import StringIO
import compiler

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
