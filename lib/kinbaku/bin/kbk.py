""" kinbaku.bin.kinbaku:  the command line script

    $ kinbaku code --path=$HOME/code --search foobar
    $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

    $ kinbaku detect --path=$HOME/code --tests

    $ kinbaku validate --path=$HOME/code

"""
import copy, sys

from pep362 import signature
from path import path

from kinbaku.util import _import
from kinbaku.util import report, is_python, groupby
from kinbaku.util import divider, remove_recursively
def fpath2namespace(fpath):
    namespace  = fpath.namebase
    if namespace == '__init__':
        namespace = fpath.dirname().namebase
    return namespace

def parser():
    """ builds the parser object """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="use FILE", metavar="FILE")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
    parser.add_option("-s", "--search", dest="search", default=True, help="..")
    parser.add_option("-p", "--path", dest="path",  default='', help="..")
    return parser

def announce_discovery(fpath,plugin_obj):
    """ placeholder """
    # print "\tfound plugin",fpath,plugin_obj, plugin_obj.__class__.__bases__
    pass

def plugin_search_results():
    """ NOTE: currently the search-path only includes kinbaku's root module """
    plugins         = []
    fileself        = path(__file__).abspath()
    container       = fileself.dirname().dirname().abspath()
    container_all   = [ x.abspath() for x in container.files() if x.abspath()!=fileself and x.namebase!='__init__']
    container_files = [ x for x in container_all if x.ext == '.py']
    module_dir      = lambda x: any([y.name=='__init__.py' for y in x.files()])
    module_roots    = [ x + path('/__init__.py') for x in container.dirs() if module_dir(x) ]

    file_options    = container_files + module_roots
    for fpath in file_options:
        reality    = globals()
        shadow     = copy.copy(globals())
        namespace  = fpath2namespace(fpath)
        shadow.update(dict(__name__=namespace))
        execfile(fpath, shadow)
        difference = list(set(shadow.keys())-set(reality.keys()))
        if "plugin" in difference:
            plugin_obj = shadow['plugin']
            plugins.append([fpath, plugin_obj])
            announce_discovery(fpath, plugin_obj)
    return plugins

def show_all_plugins():
    """ displays all plugins and their
        options in an easy to read menu """
    matches = plugin_search_results()
    print "\n Help for sub-commands:\n"
    for match in matches:
        fpath, plugin = match
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        print ' ', fpath2namespace(fpath).upper()
        #try:
        plugin_obj = plugin.spawn()
        #except TypeError, t:
        #    raise TypeError, str(t)+'\nExpectedSignature: '+str(signature(plugin_obj.__init__)._parameters)
        plugin_obj.help(indent=3)


def handle_main_argument(args, options):
    """ get a subparser and dispatch """

    try: main = args[0]
    except IndexError:
        show_all_plugins(); sys.exit()
    else:
        if main=='help':
            show_all_plugins(); sys.exit()

    try:
        import_line = 'kinbaku.{plugin}'.format(plugin=main)
        plugin_mod  = _import(import_line)
    except ImportError,e:
        err = "Plugin \"{p}\" not found: {e}"
        print err.format(p=main,e=str(e))
        sys.exit()
    else:
        plugin = getattr(plugin_mod, 'plugin',None)
        if not plugin:
            report('Code not retrieve "plugin" from {mod}',mod=plugin_mod)
            sys.exit()
        #try:
        plugin_obj = plugin.spawn()
        #except TypeError:
        #    raise Exception, signature(plugin_obj.__init__)._parameters
        plugin_obj.parse_args(args[1:], options)

def entry():
    """ """
    if "--help" in sys.argv:
        show_all_plugins(); sys.exit()
    else:
        (options, args) = parser().parse_args()
        handle_main_argument(args,options)

if __name__=='__main__':
    entry()

#codebox = '/home/matt/code/kinbaku/codebox'
#with CodeBase(codebox, gloves_off=True) as codebase:
#divider(msg='inside context')
#report("codebase", codebase) #report("  test_files: "); report(*[fname for fname in codebase])
#test_search = codebase.search("zam"); #report("  test_search: {results}",results=str(test_search))
#import IPython;IPython.Shell.IPShellEmbed(argv=[])()
#for x in test_search: print x
#print 'next', codebase.next() #search(codebase, name)
