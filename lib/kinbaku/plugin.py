""" kinbaku.plugin
"""

import copy
import sys, os

from path import path
from pep362 import signature

from kinbaku.report import report

def publish_to_commandline(func):
    """ decorator for plugin methods """
    func.is_published_to_commandline = True
    return func
def is_published_to_commandline(func):
    """ detects functions that have been marked for publishcation """
    return hasattr(func,'is_published_to_commandline')

class Plugin(object):
    """ """
    @classmethod
    def parse_args(kls, args, options):
        """ receives cascaded args/options """

        def panic():
            print
            #print kls.__module__.split('.')[-1].upper()
            kls().help()
            sys.exit()

        # NOTE: do not move import..
        from kinbaku.config import Config

        try: interface_name = args[0]
        except IndexError: ## Not even a function name
            panic()
        else: ## Got plugin name..
            try: args = args[1:]
            except IndexError: ## .. But not command.
                show_plugin_commands(interface_name)
                sys.exit()


            else: ## Got name and command!
                pass

        # Get "path" either from command line or
        #  by way of the Config-plugin.
        path = options.path
        path = path or Config().get('path', os.getcwd())

        if not (interface_name and path):
            print 'wonk'
            from kinbaku.bin.kbk import USAGE
            print USAGE
            sys.exit()

        if not os.path.exists(path):
            path = os.getcwd()

        # conversion to dictionary  from an optparser.options instance
        options = eval(str(options))
        options['path']=path
        try:
            instance = kls.spawn(**options)
        except TypeError:
            print('\nERROR: spawning {kls} with {options}'.format(
                kls=kls.__name__, options=options))
            sys.exit()

        func   = getattr(instance, interface_name,None)
        if func is None:
            panic()
        parent = kls.__name__.lower()
        if not is_published_to_commandline(func):
            err  = '\nERROR:  Interface "{I}" is not published on plugin "{P}".'
            err += '\n        For help using this plugin, try: "{progname} {P} help"'
            err  = err.format(I=interface_name, P=parent,progname=sys.argv[0],
                              )
            print err
            sys.exit()

        #report("running {f} with {a}, {k}", f=func.__name__, a=args, k=options)
        kls.display_results(func(*args))

    @publish_to_commandline
    def help(self, indent=0):
        """ shows help for this plugin """
        cls_names = [ x for x in dir(self.__class__) if \
                      is_published_to_commandline(getattr(self, x)) and\
                      x!='help' ]
        modname    = self.__class__.__module__.lower().split('.')[-1]

        if not indent:
            print "->",modname.upper()
            indent=3

        for name in cls_names:
            func       = getattr(self,name)
            doc        = func.__doc__
            parent     = self.__class__.__name__.lower()

            progname   = os.path.split(sys.argv[0])[1]
            sig        = signature(func)
            parameters = sig._parameters

            display1     = lambda k:   '<{k}>'.format(k=k)
            dvdisplay    = lambda p:   (p.default_value is not None and \
                                        '[<{k}={deflt}>'.format(**{'k':p.name,
                                                                  'deflt':p.default_value})) or \
                                       ('[<{k}>]'.format(**{'k':p.name}))
            position     = lambda k:   parameters[k].position
            sort_machine = lambda x, y: cmp(x[0],y[0])

            func_sig   = [ [position(k), k, parameters[k] ] for k in parameters.keys() ]
            func_sig.sort(sort_machine) # sort args by their position in signature

            display    = lambda t: (hasattr(t[2],'default_value') and \
                                    dvdisplay(t[2])) or \
                                   (True and \
                                    display1(t[1]))

            func_sig   = [ display(x) for x in func_sig ]
            func_sig   = func_sig[1:] # probably an instancemethod.. chop off "self"
            func_sig   = ' '.join(func_sig)
            _ex        = "{kinbaku} {plugin} {name} {sig}".format(kinbaku = progname,
                                                                  plugin  = modname,
                                                                  name    = name,
                                                                  sig     = func_sig)
            if doc:
                dox =  [x.strip() for x in doc.split('\n') if x.strip()]
            else:
                 dox = ["No documentation yet."]

            for line in dox:
                ex = _ex
                first_loop = not dox.index(line)!=0
                if first_loop:
                    ex=' '*len(_ex)
                if line.startswith('+'): line = '  ' + line[1:]
                out = ' {first}{space1}{doc}'
                out = out.format(first='',
                                 space1=' ',#*(45-len(ex)),
                                 doc='')
                out = ' '*indent + out
                if first_loop:
                    print '\n\t'+_ex
                print '\t'+out + line or ""


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
