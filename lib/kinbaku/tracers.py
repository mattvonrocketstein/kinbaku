""" kinbaku.tracers
"""
from kinbaku.report import console

#from kinbaku.snoopy import snoop

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

        caller          = frame.f_back
        toplevel        = not caller
        shadow = locals(); shadow.pop('self')
        if toplevel: self.handle_toplevel(**shadow)
        else:
            return self.handle(frame, arg, caller, co, func_name, func_filename)

    def handle_module(self,fname):
        pass


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
