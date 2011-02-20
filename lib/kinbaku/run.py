""" kinbaku.run
"""
import StringIO
import sys
from path import path
import tempfile

from rope.refactor.importutils import ImportTools, importinfo, add_import
from coverage.cmdline import main,CoverageScript


from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.codebase import plugin as CodeBase
from kinbaku._types import FileCoverage

class Run(KinbakuPlugin):
    """ """
    @publish_to_commandline
    def cvg(self, fpath):
        """ runs coverage on fpath: equivalent to
              coverage run $FPATH; coverage report $FPATH |grep $STRING
        """
        OLD_BANNER = '----------------------------------------------------------------------------------'
        fhandle    = StringIO.StringIO("")
        report_args = dict( morfs = [],
                            ignore_errors = False,
                            file = fhandle,
                            omit = '', include = '', )
        cscript = CoverageScript()
        status = cscript.command_line(['run', fpath])
        if status==0:
            cscript.coverage.report(show_missing=True, **report_args)
            fhandle.seek(0);
            results = fhandle.read()
            results = results.replace(OLD_BANNER, console.divider(display=False))
            results = [r for r in results.split('\n') if r]
            out     = []
            for r in results:
                print r
                if results.index(r)>1:
                    cvg_output_line = r.split()
                    miss,  cover      = cvg_output_line[2],cvg_output_line[3]
                    fname, statements = cvg_output_line[0],cvg_output_line[1]
                    linenos   = ''.join(cvg_output_line[4:]).split(',')
                    linenos   = map(int, linenos)
                    fpath_cvg = FileCoverage(fname=fname, statements=statements,
                                             miss=miss, cover=cover, linenos=linenos)
                    out.append(fpath_cvg)
                    print '\t',fpath_cvg

            print console.divider(display=False).strip()
            return out

        else:
            raise Exception,['not sure what to do with cvg status:',status]


plugin = Run

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
