""" kinbaku.plugin
"""

import copy
import sys, os
import inspect

from types import StringType
from types import BooleanType
from optparse import OptionParser

from path import path
from pep362 import signature

from kinbaku.python import Signature
from kinbaku.plugin.helpers import panic
from kinbaku.plugin.helpers import display
from kinbaku.plugin.helpers import str2list
from kinbaku.plugin.helpers import position
from kinbaku.plugin.helpers import dvdisplay,func2sig
from kinbaku.plugin.helpers import oparser_from_sig
from kinbaku.plugin.helpers import options2dictionary

from kinbaku.report import report, console

DEFAULT_PROGNAME = 'kinbaku'

def publish_to_commandline(func):
    """ decorator for plugin methods """
    func.is_published_to_commandline = True
    return func

def is_published_to_commandline(func):
    """ detects functions that have been marked for publishcation """
    return hasattr(func, 'is_published_to_commandline')

def get_path_from_config():
    """ Gets "path" by way of the Config-plugin.
        NOTE: do not move import..
    """
    from kinbaku.config import Config
    path = Config().get('path', os.getcwd())
    if not os.path.exists(path):
        path = os.getcwd()
    return path

class Plugin(object):
    """ Abstract Plugin """
    _parse_main = ''

    def prepare_sig(self, func, modname):
        """ prepare a legible, context-senstive signature from func """
        progname   = os.path.split(sys.argv[0])[1]
        sig_obj, sig_str = func2sig(func)
        car =  "{kinbaku} ".format(kinbaku = progname)
        if progname != DEFAULT_PROGNAME:
            plugin=''
        else:
            plugin = modname
        plugin=plugin and plugin+' '
        cdr = '{plugin}{S}'.format(S=sig_str, plugin = plugin )
        return car+cdr

    @classmethod
    def parse_args(kls, args, options, main=''):
        """ receives cascaded args/options
        """
        kls._parse_main = main
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
        mock = type("tmp",(object,),dict(secret_options={}))
        options = options2dictionary(options, mock)
        try:
            instance = kls.spawn(**options)
        except TypeError:
            print('\nERROR: spawning {kls} with {options}'.format(
                kls = kls.__name__, options=options))
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
            options    = options2dictionary(options, parser)
            kargs      = options

            # clean up things that are in both args/kargs because
            #  of the weird way this stuff is getting parsed..
            #if len(args) >= len(kargs):
            for v in kargs.values():
                if str(v) in args:
                    args.pop(args.index(str(v)))

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
        print args, kargs
        result = func(*args, **kargs) #kls.display_results(result)


    def get_subcommands(self):
        """ """
        return [ x for x in dir(self.__class__) if \
                 is_published_to_commandline(getattr(self, x)) and \
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

            _ex = console.blue(self.prepare_sig(func, modname))

            if doc: dox = filter(None, [x.strip() for x in doc.split('\n')] )
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
                    print '\t' + _ex
                print '\t'+ out + line or ""
        return cls_names

    @classmethod
    def spawn(kls, **kargs): return kls(**kargs)

    @staticmethod
    def display_results(result):
       """
       """
       if isinstance(result, list):
           for x in result:
               print '  ', x
       elif isinstance(result, dict):
           report(**result)
       else:
           pass
KinbakuPlugin = Plugin
