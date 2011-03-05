""" kinbaku.snoopy

    Tools for running and tracing python code
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
"""

import os
import inspect

from kinbaku.tracers import CallTracer
from kinbaku._functools import Fingerprint
from kinbaku.report import console
from kinbaku.python import is_atom

SNOOP_REGISTRY = []

def snoop(func):
    """ decorator for snooped functions """
    global SNOOP_REGISTRY
    fingerprint = Fingerprint.build_from(func)
    SNOOP_REGISTRY += [fingerprint]
    func.io_snoop = True
    return func

class Snooper(CallTracer):
    """ Simple tracer for python code.. will be invoked only for
        functions that have been decorated with snoop(), or functions
        that match patterns describes by "names"/"files"
    """
    def __init__(self, names=[],files=[]):
        """ """
        self._record = []
        self.files   = files
        self.names   = names

    def is_snooped(self, func_name=None, func_filename=None, func=None):
        """ detects functions that have been marked for snooping """
        confessed        = hasattr(func, 'io_snoop')
        have_fingerprint = Fingerprint(func_name=func_name,
                                       func_filename=func_filename) in SNOOP_REGISTRY
        return confessed or have_fingerprint

    def is_nearby(self, fname):
        """ arbitrary measure of "closeness" """
        return fname in self.files

    @property
    def watched(self):
        """ """
        function_is_decorated = Fingerprint(func_name=self.func_name,
                                            func_line_no=self.func_line_no,
                                            func_filename=self.func_filename) \
                                in SNOOP_REGISTRY

        out = function_is_decorated or \
              ( self.is_nearby(self.func_filename) and any([name in self.func_name for name in self.names]))
        if not out:
            pass#rint "ignoring ",self.func_filename,self.func_name,self.is_nearby(self.func_filename)
        return out
    def handle(self):
        """ called by CallTracer.__call__, this is the main
            event-responder entry for this tracer """
        if not self.watched: return
        else:
            msg = '  In function: "{fname}"\n    {cline}:{cfile} ---> {fline}:{fpath}'
            msg = msg.format(fname = console.red(str(self.func_name)),
                             fline = console.blue(str(self.func_line_no)),
                             fpath = console.red(str(self.func_filename)),
                             cline = console.blue(str(self.caller_line_no)),
                             cfile = console.red(str(self.caller_filename)))
            print msg
            return self.trace_lines

    def trace_lines(self, frame, event, arg):
        """ called for line return/line events """
        self.frame=frame; self.event=event;self.arg=arg
        if event not in ['line','return']: return
        if event=='return':
            return self.trace_return(frame,event,arg)
        co = self.co
        filename = co.co_filename
        msg = 'line {fline}:\t {locals}'
        msg = msg.format(fname=self.func_name, fline=console.blue(str(self.line_no)),
                         locals=console.color(str(frame.f_locals))).strip()
        hdr = console.red('    ::  ')
        print hdr + msg
        return self.trace_lines

    def trace_return(self, frame, event, arg):
        """ called for return events """
        self.arg=arg
        self.frame=frame;
        self.event=event;
        _rv = str(self.return_value)
        if is_atom(arg):
            print console.red ('    -> atom: ') + console.color(_rv)
            self.record()
        else:
            print console.blue('    -> composite: ') + console.color(_rv)
        return

    def record(self):
        """ """
        if self.is_class_definition:
            print >>sys.stderr,"ignoring class def",self.func_name
        fprint = Fingerprint(func_name     = self.func_name,
                             func_filename = self.func_filename,
                             func_line_no  = self.func_line_no,
                             func_vals     = self.vals,
                             return_value  = self.return_value)
        self._record.append(fprint)
