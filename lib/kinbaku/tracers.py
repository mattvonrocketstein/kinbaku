""" kinbaku.tracers
"""

import os
import inspect

from pythoscope.tracer import is_class_definition

class PythonFrame(object):
    """ wrapper for python frame """
    @property
    def func_line_no(self):    return self.frame.f_lineno
    lineno = func_line_no
    line_no = func_line_no
    line   = func_line_no

    @property
    def vals(self):
        x = inspect.getargvalues(self.frame)
        return x.args
        #arguments = dict([ [arg, str(x.locals[arg])] for arg in  x.args ])
        #return arguments


    @property
    def caller_line_no(self):  return self.caller and self.caller.f_lineno
    @property
    def caller_filename(self): return self.caller and self.caller.f_code.co_filename

    @property
    def co(self):
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return self.frame.f_code
    @property
    def locals(self): return frame.f_locals
    @property
    def func_filename(self): return self.co and os.path.abspath(self.co.co_filename)
    @property
    def caller(self): return self.frame.f_back

    @property
    def return_value(self):
        """ only true if event==return """
        return self.arg
    @property
    def func_name(self): return self.co.co_name

    @property
    def toplevel(self):  return not self.caller

    @property
    def is_class_definition(self):
        return is_class_definition(self.frame)

class Tracer(PythonFrame):
    """ tracer for use with sys.settrace """

    def __call__(self,frame,event,arg):
        pass

class CallTracer(Tracer):
    """ """

    def __call__(self, frame, event, arg):
        """ """
        self.frame = frame
        self.event = event
        self.arg   = arg
        if self.event != 'call':
            return
        elif self.func_name == 'write':
            return # Ignore write() calls from print statements
        elif self.func_name=='<module>':
            return self.handle_module(self.func_filename)
        elif self.toplevel:
            return self.handle_toplevel()
        else:
            return self.handle()

    def handle_toplevel(self):
        """ called only for module-level "calls"..
            the way the sys.settrace works is weird """
        pass

    def handle_module(self, fname):
        """ """
        pass
