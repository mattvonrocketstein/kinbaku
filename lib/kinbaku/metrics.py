""" kinbaku.metrics
"""

from path import path
from pygenie.cc import measure_complexity, PrettyPrinter

from kinbaku.plugin import KinbakuPlugin
from kinbaku.report import console,report
from kinbaku.core import KinbakuFile
from kinbaku.codebase.codebase import CodeBase
from kinbaku.plugin import publish_to_commandline

class SimplePlugin(KinbakuPlugin):
    """ takes no arguments to spawn """
    @classmethod
    def spawn(kls, **kargs):
        return kls()

class Metrics(SimplePlugin):
    """ code metrics plugin """

    @publish_to_commandline
    def hall_of_shame(self, fpath, cutoff=3, maxnum=10):
        """ shows the most complex parts of the code in fpath """
        results = self._hall_of_shame(fpath, cutoff=cutoff, maxnum=maxnum)
        for fpath, stats in results:
            print
            print console.blue(fpath)
            console.divider()
            for x, y, z in stats:
                print z, x, y
            console.divider()

    def _hall_of_shame(self, fpath, cutoff=3, maxnum=10):
        """ show the most complex entries in fpath """
        out =  []
        results = self._complexity(fpath)

        for fpath, stats in results.items():
            if isinstance(stats,dict):
                stats = stats[fpath.abspath()]

            if stats is None: continue
            if not stats: continue

            stats = [ [_type, dotpath, score ]
                      for _type, dotpath, score in stats
                      if score > cutoff ]
            stats.sort(lambda x, y: cmp(x[-1], y[-1]))
            out.append( [ fpath, stats ] )
        results = filter(lambda x: x[1], results)
        results.sort(lambda x,y: cmp(max([z[-1] for z in x[1]]),
                                     max([z[-1] for z in y[1]])))
        return out


    @publish_to_commandline
    def complexity(self, fname, files=True, methods=True, classes=True):
        """ shows cyclomatic complexity statistics for files, methods, and classes.
            passing any of --files, --methods, --classes leaves those types of
            objects out of reporting. """
        out = self._complexity(fname, files=files, methods=methods, classes=classes)
        for fpath, results in out.items():
            print '\n', console.blue(fpath), '\n', console.divider(display=False)
            if isinstance(results,dict):
                results = results[results.keys()[0]]
            for _type, dotpath, score in results:
                print score, console.blue(_type), console.red(dotpath)
            console.divider()

    def _complexity(self, *args, **kargs):
        return dict(self._zcomplexity(*args, **kargs))

    def _zcomplexity(self, fname, files=True,
                     methods=True, classes=True):
        """ """
        if path(fname).isdir():
            out = []
            for fpath in CodeBase(path(fname),gloves_off=True).python_files:
                stats = self._complexity(fpath, files=files,
                                         methods=methods, classes=classes)
                out += [ [ fpath, stats ] ]
            return out
        out = KinbakuFile(fname).complexity()

        if not methods: out = filter(lambda item: item[0] != 'method', out)
        if not files:   out = filter(lambda item: item[0] != 'file',   out)
        if not classes: out = filter(lambda item: item[0] != 'class',  out)
        return [ [ path(fname).abspath(), out ] ]

plugin = Metrics
