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

OLD_BANNER = '----------------------------------------------------------------------------------'

class Run(KinbakuPlugin):
    """ """

    def _cvg(self, fpath, exclude=''):
        """ returns header,[ filecoverage_obj, ..] """

        if isinstance(exclude,str): exclude=filter(None,exclude.split())
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
            def convert(x):
                if not x: return
                try: return int(x)
                except ValueError:
                    return map(int,x.split('-'))
            for r in results:
                #print r
                if results.index(r)>1:
                    cvg_output_line = r.split()
                    miss,  cover      = cvg_output_line[2],cvg_output_line[3]
                    fname, statements = cvg_output_line[0],cvg_output_line[1]
                    if fname=='TOTAL': print ''.join(r);continue
                    linenos   = ''.join(cvg_output_line[4:]).split(',')
                    linenos   = map(convert, linenos)
                    # NOTE: cuts off the "missed lines" bit, it's stored in "linenos"
                    original_line = r.split('%')[0]+'%'
                    fpath_cvg = FileCoverage(fname=fname, statements=statements,
                                             original_line=original_line,
                                             miss=miss, cover=cover,
                                             linenos=linenos)
                    if exclude:
                        if not any([filtr in fname for filtr in exclude]):
                            out.append(fpath_cvg)
                    else:
                        out.append(fpath_cvg)

            header=results[0]
            return header[:header.rfind(' ')],out

        else:
            raise Exception,['not sure what to do with cvg status:',status]


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
            print ' ', fpath_coverage.original_line
            #print '\t', fpath_coverage.affected() #_ast, affected = fpath_coverage.affected()
            if objects:
                print '   Objects missing from coverage:'
                for lineno,line in fpath_coverage.objects_missing_from_coverage():
                    print '\t{lineno}: {line}'.format(lineno=lineno,line=line)

            if lines:
                print '   Lines missing from coverage:'
                for lineno,line in fpath_coverage.lines_missing_from_coverage():
                    print '\t{lineno}: {line}'.format(lineno=lineno,line=line)

        print console.divider(display=False)

plugin = Run

#if __name__=='__main__':
#    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
