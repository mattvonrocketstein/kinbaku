""" kinbaku.snoopy

    Tools for running and tracing python code
"""

import os
import inspect

from kinbaku.tracers import CallTracer
from kinbaku._functools import Fingerprint
from kinbaku.report import console

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
        functions that have been decorated with snoop()
    """
    def is_snooped(self, func_name=None, func_filename=None, func=None):
        """ detects functions that have been marked for snooping """
        confessed        = hasattr(func, 'io_snoop')
        have_fingerprint = Fingerprint(func_name,func_filename) in SNOOP_REGISTRY
        return confessed or have_fingerprint

    def handle_toplevel(self, **kargs):
        """ called only for module-level "calls"..
            the way the sys.settrace works is weird """
        pass

    def handle(self, frame, arg, caller, co, func_name, func_filename):
        """ called by CallTracer.__call__, this is the main
            event-responder entry for this tracer """
        func_line_no    = frame.f_lineno
        caller_line_no  = caller and caller.f_lineno
        caller_filename = caller and caller.f_code.co_filename
        watched         = Fingerprint(func_name, os.path.abspath(func_filename)) in SNOOP_REGISTRY
        if not watched: return
        else:
            msg = '  In function: "{fname}"\n    {cline}:{cfile} ---> {fline}:{fpath}'
            msg = msg.format(fname = console.red(str(func_name)),
                             fline = console.blue(str(func_line_no)),
                             fpath = console.red(str(func_filename)),
                             cline = console.blue(str(caller_line_no)),
                             cfile = console.red(str(caller_filename)))
            print msg
            return self.trace_lines

    def trace_lines(self, frame, event, arg):
        if event not in ['line','return']: return
        if event=='return':
            return self.trace_return(frame, event, arg)
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno

        filename = co.co_filename

        msg = 'line {fline}:\t {locals}'
        msg = msg.format(fname=func_name, fline=console.blue(str(line_no)),
                         locals=console.color(str(frame.f_locals))).strip()
        hdr = console.red('    ::  ')
        print hdr+msg
        return self.trace_lines

    def trace_return(self, frame, event, arg):
        """ """
        if arg==eval(repr(arg)):
            print console.red ('    -> atom: ') + console.color(str(arg))
        else:
            print console.blue('    -> composite: ') + console.color(str(arg))
        return
