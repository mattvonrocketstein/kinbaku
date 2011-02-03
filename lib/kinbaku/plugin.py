import sys
import os
from kinbaku.report import report

def publish_to_commandline(func):
    """ """
    func.is_published_to_commandline = True
    return func

def is_published_to_commandline(func):
    return hasattr(func,'is_published_to_commandline')

class KinbakuPlugin(object):
    """ """

    @classmethod
    def parse_args(kls, args, options):
        """ receives cascaded args/options """
        from kinbaku.config import Config

        if not args:
            report("Expected args")
        try:
            name, args = args[0], args[1:] # SNIP
        except IndexError:
            report("Expected ie codebase search")
            sys.exit()

        path = options.path
        path = path or Config().get('path', os.getcwd())

        if not (name and path):
            from kinbaku.bin.kbk import USAGE
            #print "bad name/path combo", name, path
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
        func = getattr(instance, name)
        #report("running {f} with {a}, {k}", f=func.__name__, a=args, k=options)
        kls.display_results(func(*args))

    @publish_to_commandline
    def help(self):
        """ """
        from pep362 import signature
        cls_names = [ x for x in dir(self.__class__) if \
                      is_published_to_commandline(getattr(self, x)) and\
                      x!='help' ]
        for name in cls_names:
            space    = ' '
            func     = getattr(self,name)
            doc      = func.__doc__
            parent   = self.__class__.__name__.lower()
            progname = os.path.split(sys.argv[0])[1]
             # probably an instancemethod..
            func_sig = ['@'+k for k in signature(func)._parameters.keys() if k!='self']
            _ex      = "{kinbaku} {plugin} {name} {sig}".format(kinbaku = progname,
                                                                plugin  = parent,
                                                                name    = name,
                                                                sig     = func_sig)
            print space,_ex,'\n', space*2, doc
            print

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
