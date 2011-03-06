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
    """ """
    @publish_to_commandline
    def complexity(self, fname, files=True, methods=True, classes=True):
        """ shows cyclomatic complexity statistics for files, methods, and classes.
            passing any of --files, --methods, --classes leaves those types of
            objects out of reporting. """
        if path(fname).isdir():
            for fpath in CodeBase(path(fname),gloves_off=True).python_files:
                print '\n',console.blue(fpath)
                console.divider()
                self.complexity(fpath, files=files, methods=methods, classes=classes)
            return
        out = KinbakuFile(fname).complexity()
        if not methods: out = filter(lambda item: item[0] != 'method', out)
        if not files:   out = filter(lambda item:   item[0] != 'file', out)
        if not classes: out = filter(lambda item: item[0] != 'class', out)
        for _type, dotpath, score in out:
            print score, console.blue(_type), console.red(dotpath)

plugin=Metrics
