""" kinbaku.metrics
"""
from StringIO import StringIO
from path import path
from pygenie.cc import measure_complexity, PrettyPrinter

from kinbaku.plugin import KinbakuPlugin
from kinbaku.report import console,report
from kinbaku.plugin import publish_to_commandline

class SimplePlugin(KinbakuPlugin):
    """ takes no arguments to spawn """
    @classmethod
    def spawn(kls, **kargs):
        return kls()

class Metrics(SimplePlugin):
    """ """
    @publish_to_commandline
    def cyclo(self, fname):
        """cyclomatic complexity statistics """
        def gettype(x):
            if x=='X': return 'file'
            if x=='M': return 'method'
            if x=='C': return 'class'
        def getpath(_type,dotpath):
            if _type=='X': return path(dotpath).abspath()
            return dotpath

        out = self._cyclo(fname)
        out = [[gettype(_type), getpath(_type,dotpath), score] for _type,dotpath,score in out]
        for _type,dotpath,score in out:
            print score, console.blue(_type), console.red(dotpath)

    def _cyclo(self, fname):
        """
            [('X', 'some/path/name.py', complexity_score),
             ('C', 'MedleyWeatherAlert', complexity_score),
             ('M', 'MedleyWeatherAlert.__str__', complexity_score),
            ]

        """
        code = open(fname).read()
        stats = measure_complexity(code, fname)
        return PrettyPrinter(StringIO()).flatten_stats(stats)
        #for x in stats.classes:
        #    print str(x)

plugin=Metrics
