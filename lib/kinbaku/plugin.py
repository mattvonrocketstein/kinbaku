""" kinbaku.plugin
"""

import copy
import sys, os
import inspect

from types import BooleanType,StringType
from optparse import OptionParser

from path import path
from kinbaku._types import Signature
from pep362 import signature

from kinbaku.report import report,console
position     = lambda parameters, k:   parameters[k].position
display1     = lambda k:   '<{k}>'.format(k=k)
def dvdisplay(p):
    """ default-value display for parameter p """
    fmt = {'k':p.name,
           'deflt':p.default_value}
    if p.default_value is not None:
        return '[<{k}={deflt}>]'.format(**fmt)
    else:
        return ('[<{k}>]'.format(**{'k':p.name}))

def prepare_sig(func,modname):
    """ prepare a legible, context-senstive signature from func """
    progname   = os.path.split(sys.argv[0])[1]
    sig        = signature(func)
    parameters = sig._parameters

    sort_machine = lambda x, y: cmp(x[0],y[0])
    func_sig   = [ [position(parameters, k), k, parameters[k] ] for k in parameters.keys() ]
    func_sig.sort(sort_machine) # sort args by their position in signature

    func_sig   = [ display(x) for x in func_sig ]
    func_sig   = func_sig[1:] # probably an instancemethod.. chop off "self"
    func_sig   = ' '.join(func_sig)

    _ex = "{kinbaku} {plugin} {name} {sig}"
    _ex = _ex.format(kinbaku = progname, name = sig.name,
                             plugin = modname, sig = func_sig)
    return _ex

def display(t):
    if hasattr(t[2],'default_value'):
        return dvdisplay(t[2])
    else:
        return display1(t[1])

def options2dictionary(options):
    """ conversion to dictionary  from an optparser.options instance """
    options         = eval(str(options))
    return options

def publish_to_commandline(func):
    """ decorator for plugin methods """
    func.is_published_to_commandline = True
    return func

def is_published_to_commandline(func):
    """ detects functions that have been marked for publishcation """
    return hasattr(func,'is_published_to_commandline')

def panic(kls):
    print; kls().help();
    sys.exit()

def get_path_from_config():
    """ Gets "path" by way of the Config-plugin.
        NOTE: do not move import..
    """
    from kinbaku.config import Config
    path = Config().get('path', os.getcwd())
    if not os.path.exists(path):
        path = os.getcwd()
    return path

def oparser_from_sig(func_sig):
    """ """
    class Foo(OptionParser):
        pass
    obj=Foo()
    for name,val in func_sig.default_values.items():
        kargs = dict(dest=name, metavar=name.upper())
        if isinstance(val,BooleanType):
            if val: kargs.update(dict(default=val, action="store_false"))
            else:   kargs.update(dict(default=val, action="store_true"))
        if isinstance(val, StringType):
            kargs.update(default=val)
        else:
            kargs={} # abort.. not sure what to do yet
            #raise Exception,[name,val]
        if kargs:
            obj.add_option("--"+name, **kargs)
    return obj

class Plugin(object):
    """ Abstract Plugin """
    @classmethod
    def parse_args(kls, args, options):
        """ receives cascaded args/options """
        try: interface_name = args[0]
        except IndexError: ## Not even a function name
            panic(kls)
        else: ## Got plugin name..
            try: args = args[1:]
            except IndexError: ## .. But not command.
                show_plugin_commands(interface_name)
                sys.exit()

            else: ## Got name and command!
                pass

        path = get_path_from_config()

        if not (interface_name and path):
            from kinbaku.bin.kbk import USAGE
            print USAGE
            sys.exit()

        options = options2dictionary(options)
        try:
            instance = kls.spawn(**options)
        except TypeError:
            print('\nERROR: spawning {kls} with {options}'.format(
                kls=kls.__name__, options=options))
            sys.exit()

        func   = getattr(instance, interface_name, None)
        if func is None: panic(kls)
        func_sig = signature(func)

        # if this function has default values, we'll dynamically
        # generate an appropriate options-parser to use those values
        if func_sig.has_default_values:
            # discards the arguments, keeping original
            parser     = oparser_from_sig(func_sig)
            options, _ = parser.parse_args()
            options    = options2dictionary(options)
            kargs      = options

            # clean up things that are in both args/kargs because
            #  of the weird way this stuff is getting parsed..
            if len(args)>len(kargs):
                for v in kargs.values():
                    if v in args:
                        args.pop(args.index(v))

            # answer "help" in a context-sensitive way if it's
            # somewhere on the command line
            if args and 'help' in args:
                print "Help for {func_sig}".format(func_sig='.'.join([instance.__class__.__name__,interface_name]))
                parser.print_help()
                sys.exit()
        else:
            kargs = {}

        parent = kls.__name__.lower()
        if not is_published_to_commandline(func):
            err  = '\nERROR:  Interface "{I}" is not published on plugin "{P}".'
            err  = console.red(error)
            err += '\n        For help using this plugin, try: "{progname} {P} help"'
            fmt  = dict(I=interface_name, P=parent, progname=sys.argv[0],)
            err  = err.format(**fmt)
            print err
            sys.exit()

        #print args,kargs
        result = func(*args, **kargs) #kls.display_results(result)

    def get_subcommands(self):
        """ """
        return [ x for x in dir(self.__class__) if \
                 is_published_to_commandline(getattr(self, x)) and\
                 x!='help' ]

    @publish_to_commandline
    def help(self, indent=0):
        """ shows help for this plugin """

        cls_names = self.get_subcommands()
        modname   = self.__class__.__module__.lower().split('.')[-1]
        if not indent:
            print "->", modname.upper()
            indent=3

        for name in cls_names:
            func       = getattr(self,name)
            doc        = func.__doc__
            parent     = self.__class__.__name__.lower()

            _ex = console.blue(prepare_sig(func,modname))

            if doc: dox =  filter(None, [x.strip() for x in doc.split('\n')] )
            else:   dox = [ "No documentation yet." ]

            for line in dox:
                ex = _ex
                first_loop = not dox.index(line)!=0
                if first_loop:           ex   = ' '*len(_ex)
                if line.startswith('+'): line = '  ' + line[1:]
                out = '{indent} {first}{space1}{doc}'
                out = out.format(first='',doc ='',
                                 space1=' ',#*(45-len(ex)),
                                 indent = ' '*indent,)
                if first_loop:
                    print '\t'+ _ex
                print '\t'+ out + line or ""
        return cls_names

    @classmethod
    def spawn(kls, **kargs): return kls(**kargs)

    @staticmethod
    def display_results(result):
       """
            console.draw_line(msg="inside context")
            report("codebase", codebase) #report("  test_files: "); report(*[fname for fname in codebase])
            test_search = codebase.search("zam"); #report("  test_search: {results}",results=str(test_search))
            import IPython;IPython.Shell.IPShellEmbed(argv=[])()
       """
       if isinstance(result,list):
           #report(*result)
           for x in result:
               print '  ',x
       elif isinstance(result,dict):
           report(**result)
       else:
           pass
           #report("Not sure how to deal with answer:", result)
KinbakuPlugin = Plugin



#show_all_plugins()
