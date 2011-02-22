""" kinbaku.run
    TODO: support in kbkplugin for kbk run <fpath> == kbk run trace <fpath>
"""

import sys
from path import path
import tempfile

from rope.refactor.importutils import ImportTools, importinfo, add_import
from coverage.cmdline import main,CoverageScript

from kinbaku._types import FileCoverage
from kinbaku.report import console, report
from kinbaku.codebase import plugin as CodeBase
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline, str2list
from kinbaku._coverage import KinbakuFile, OLD_BANNER, convert, mine_cvg_output
from kinbaku.snoopy import Snooper

class CLI(KinbakuPlugin):
    @publish_to_commandline
    def recordio(self,fpath):
        """ pass """

    @publish_to_commandline
    def trace(self, fpath):
        """ dynamically analyze programs IO traffic """
        print ' ',console.red('tracing'),fpath
        sys.settrace(Snooper())
        execfile(fpath)


    @publish_to_commandline
    def cvg(self, fpath, objects=False, lines=False, containers=False, exclude=''):
        """ runs coverage on <fpath>:
               when lines is True, will show lines that are missing
               from coverage. when "containers" is True, will show
               methods or classes that are missing from coverage.
               if "exclude" is given, then filenames not matching
               will not be included in the output.
        """
        header, results = self._cvg(fpath,exclude=exclude)
        print ' {hdr}\n{div}'.format(hdr=header,div=console.divider(display=False))
        for fpath_coverage in results:
            print ' ',  fpath_coverage.original_line
            if objects:
                self.handle_objects(fpath_coverage)
            elif lines:
                self.handle_lines(fpath_coverage)

class Run(CLI):
    """ """
    def _cvg(self, fpath, exclude=''):
        """ returns header,[ filecoverage_obj, ..] """
        out     = []
        exclude = str2list(exclude)
        results = KinbakuFile(fpath).run_cvg()

        results = results.replace(OLD_BANNER, console.divider(display=False))
        results = [r for r in results.split('\n') if r]

        for r in results:
            if not results.index(r)>1: continue
            fname, miss, cover, linenos, original_line, statements = mine_cvg_output(r)

            if fname=='TOTAL':
                print ''.join(r)
                continue

            fc_kargs = dict( fname=fname, statements=statements,
                             original_line=original_line, miss=miss,
                             cover=cover, linenos=linenos )

            fpath_cvg = FileCoverage(**fc_kargs)
            if exclude:
                if not any([filtr in fname for filtr in exclude]):
                    out.append(fpath_cvg)
            else:   out.append(fpath_cvg)

        header = results[0]
        return header[:header.rfind(' ')],out

    @staticmethod
    def handle_objects(coverage_obj):
        print '   Objects missing from coverage:'
        lst1 = coverage_obj.objects_missing_from_coverage()
        lst2 = coverage_obj.lines_missing_from_coverage()
        tmp=lst1+lst2
        tmp.sort(lambda x,y: cmp(x[0],y[0]))
        for lineno, line in tmp:
            print '\t{lineno}: {line}'.format(lineno=lineno,line=line)

    @staticmethod
    def handle_lines(coverage_obj):
        print '   Lines missing from coverage:'
        for lineno,line in coverage_obj.lines_missing_from_coverage():
            print '\t{lineno}: {line}'.format(lineno=lineno,line=line)
        print console.divider(display=False)

plugin = Run

#if __name__=='__main__':
#    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
