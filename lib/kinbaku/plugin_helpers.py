""" plugin_helpers
"""

import sys

from optparse import OptionParser

from types import BooleanType,StringType

position     = lambda parameters, k:   parameters[k].position
display1     = lambda k:   '<{k}>'.format(k=k)

from pep362 import signature
def func2sig(func):
    """ returns sig_obj, sig_str """

    sig          = signature(func)
    parameters   = sig._parameters
    sort_machine = lambda x, y: cmp(x[0],y[0])
    func_sig     = [ [position(parameters, k), k, parameters[k] ] for k in parameters.keys() ]
    func_sig.sort(sort_machine) # sort args by their position in signature

    func_sig   = [ display(x) for x in func_sig ]
    func_sig   = func_sig[1:] # probably an instancemethod.. chop off "self"
    func_sig   = ' '.join(func_sig)
    sig_str    = "{name} {sig}".format(name=sig.name,sig=func_sig)
    return sig, sig_str

def oparser_from_sig(func_sig):
    """ dynamically generates option-parser
        subclass for function signature """
    class Foo(OptionParser):
        pass
    obj=Foo()
    for name,val in func_sig.default_values.items():
        kargs = dict(dest=name, metavar=name.upper())
        if isinstance(val,BooleanType):
            if val: kargs.update(dict(default=val, action="store_false"))
            else:   kargs.update(dict(default=val, action="store_true"))
        elif isinstance(val, StringType):
            kargs.update(default=val)
        else:
            kargs={} # abort.. not sure what to do yet
            #raise Exception,[name,val]
        if kargs:
            obj.add_option("--"+name, **kargs)
    return obj

def display(t):
    """ """
    if hasattr(t[2],'default_value'):
        return dvdisplay(t[2])
    else:
        return display1(t[1])

def options2dictionary(options):
    """ conversion to dictionary  from an optparser.options instance """
    options         = eval(str(options))
    return options

def dvdisplay(p):
    """ default-value display for parameter p """
    fmt = {'k':p.name,
           'deflt':p.default_value}
    if p.default_value is not None:
        return '[<{k}={deflt}>]'.format(**fmt)
    else:
        return ('[<{k}>]'.format(**{'k':p.name}))

def panic(kls):
    """ """
    print; kls().help();
    sys.exit()

def str2list(x,split=' '):
    """ """
    if isinstance(x,list):
        return x
    if isinstance(x, str):#StringType
        return filter(None,x.split(split))
