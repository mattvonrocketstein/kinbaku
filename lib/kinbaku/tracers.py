""" kinbaku.tracers
"""
import os
import inspect
import sys
from kinbaku.report import console
SNOOP_REGISTRY = []

class Fingerprint(object):
    def __str__(self):
        return "F:"+str(tuple([self.func_name,self.path]))
    def __repr__(self):
        return str(self)

    def __equal__(self,other):
        return self.func_name==other.func_name and self.path==os.path.abspath(other.path)

    __eq__=__equal__

    @classmethod
    def build_from(kls, func):
        return Fingerprint(func.func_name, inspect.getfile(func), func=func)

    def __init__(self, func_name=None, path=None, func=None):
        """ """
        self.func_name = func_name
        self.path      = os.path.abspath(path)
        self.func      = func

def snoop(func):
    """ decorator for snooped functions """
    global SNOOP_REGISTRY
    fingerprint = Fingerprint.build_from(func)
    SNOOP_REGISTRY += [fingerprint]
    func.io_snoop = True
    return func

class Tracer(object):
    """ tracer for use with sys.settrace """
    def __call__(self,frame,event,arg):
        pass

class CallTracer(Tracer):

    def __call__(self, frame, event, arg):
        if event!='call': return
        co            = frame.f_code
        func_name     = co.co_name
        func_filename = co.co_filename


        if func_name == 'write': return
        # Ignore write() calls from print statements

        if func_name=='<module>': return self.handle_module(func_filename)
        else: return self.handle(frame, arg, co, func_name, func_filename)

    def handle_module(self,fname):
        pass

class Snooper(CallTracer):
    """ """
    def is_snooped(self, func_name=None, func_filename=None, func=None):
        """ detects functions that have been marked for snooping """
        confessed        = hasattr(func, 'io_snoop')
        have_fingerprint = Fingerprint(func_name,func_filename) in SNOOP_REGISTRY
        return confessed or have_fingerprint

    def handle_toplevel(self, **kargs):
        """ """
        pass

    def handle(self, frame, arg, co, func_name, func_filename):
        """ """
        func_line_no    = frame.f_lineno
        caller          = frame.f_back
        toplevel        = not caller
        caller_line_no  = caller and caller.f_lineno
        caller_filename = caller and caller.f_code.co_filename
        watched         = Fingerprint(func_name, os.path.abspath(func_filename)) in SNOOP_REGISTRY
        if not watched: return

        if toplevel: self.handle_toplevel(**locals())
        else: return self.snoop(frame, func_name,
                         func_line_no,
                         func_filename,
                         caller_line_no,
                         caller_filename)


    def snoop(self, frame, func_name, func_line_no, func_filename,
              caller_line_no, caller_filename,):
        msg = '  In function: "{fname}"\n    {cline}:{cfile} ---> {fline}:{fpath}'
        msg = msg.format(fname = console.red(str(func_name)),
                         fline = console.blue(str(func_line_no)),
                         fpath = console.red(str(func_filename)),
                         cline = console.blue(str(caller_line_no)),
                         cfile = console.red(str(caller_filename)))
        print msg
        return trace_lines

def trace_lines(frame, event, arg):
    if event not in ['line','return']: return
    if event=='return':
        return trace_return(frame,event,arg)
    co = frame.f_code
    func_name = co.co_name
    line_no = frame.f_lineno
    filename = co.co_filename

    msg = 'line {fline}:\t {locals}'
    msg = msg.format(fname=func_name, fline=console.blue(str(line_no)),
                     locals=console.color(str(frame.f_locals))).strip()
    hdr = console.red('    ::  ')
    print hdr+msg
    return trace_lines

def trace_return(frame, event, arg):
    """ """
    if arg==eval(repr(arg)):
        print console.red ('    -> atom: ') + console.color(str(arg))
    else:
        print console.blue('    -> composite: ') + console.color(str(arg))
    return

    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
"""

import sys
import functools

def withlocals(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        f_locals = {}
        def probe(frame, event, arg):
            if event == 'return':
                f_locals.update(frame.f_locals)
                return probe
            sys.settrace(probe)
            try: res = f(*args,**kwds)
            finally: sys.settrace(None)
            return (res, f_locals)
    return wrapper

# example

@withlocals
def foo(x, y=0, *args, **kwds):
a = max(x,y)
b = len(args)
c = min(kwds.values())
return a+b+c

r,locs = foo(1,2,3,4,a=5,b=6)
print locs
"""
