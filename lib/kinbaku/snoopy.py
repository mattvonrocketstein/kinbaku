""" kinbaku.snoopy

    Tools for running and tracing python code
"""

import os
import inspect

from kinbaku.tracers import CallTracer
from kinbaku._functools import Fingerprint
from kinbaku.report import console

SNOOP_REGISTRY = []

def is_atom(arg):
    """ an argument is an atom iff it is
        equal to the evaluation of it's
        representation """
    return arg==eval(repr(arg))

def snoop(func):
    """ decorator for snooped functions """
    global SNOOP_REGISTRY
    fingerprint = Fingerprint.build_from(func)
    SNOOP_REGISTRY += [fingerprint]
    func.io_snoop = True
    return func

class Snooper(CallTracer):
    """ Simple tracer for python code.. will be invoked only for
        functions that have been decorated with snoop()
    """
    def __init__(self):
        self._record = []

    def is_snooped(self, func_name=None, func_filename=None, func=None):
        """ detects functions that have been marked for snooping """
        confessed        = hasattr(func, 'io_snoop')
        have_fingerprint = Fingerprint(func_name,func_filename) in SNOOP_REGISTRY
        return confessed or have_fingerprint

    @property
    def watched(self):
        return Fingerprint(func_name=self.func_name,
                           func_filename=self.func_filename) in SNOOP_REGISTRY

    def handle(self):
        """ called by CallTracer.__call__, this is the main
            event-responder entry for this tracer """
        #func_line_no    = frame.f_lineno
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
        if event not in ['line','return']: return
        if event=='return':
            return self.trace_return()
        co = self.co #frame.f_code
        func_name = self.func_name #co.co_name
        line_no = self.line_no #frame.f_lineno

        filename = co.co_filename

        msg = 'line {fline}:\t {locals}'
        msg = msg.format(fname=func_name, fline=console.blue(str(line_no)),
                         locals=console.color(str(frame.f_locals))).strip()
        hdr = console.red('    ::  ')
        print hdr+msg
        return self.trace_lines

    def record(self):
        """ """
        print Fingerprint(func_name     = self.func_name,
                          func_filename = self.func_filename,
                          return_value  = self.return_value)
        #Fingerprint(func_name=self.func_name,
        #             path=None,
        #            func=None)
        #self._record.append([filename,

    def trace_return(self):
        """ """
        if is_atom(self.arg):
            print console.red ('    -> atom: ') + console.color(str(self.arg))
            self.record()
        else:
            print console.blue('    -> composite: ') + console.color(str(self.arg))
        return
