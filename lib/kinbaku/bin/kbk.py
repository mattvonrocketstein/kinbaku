#!/usr/bin/env python
""" kinbaku.bin.kinbaku:  the command line script
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
    class Parser(OptionParser):
        def error(self, msg):
            pass

    parser = Parser()
    #parser.add_option("-f", "--file", dest="filename", help="use FILE", metavar="FILE")
    #parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
    #parser.add_option("-s", "--search", dest="search", default=True, help="..")
    #parser.add_option("-p", "--path", dest="path",  default='', help="..")
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
    #print "\n Help for sub-commands:\n"
    for match in matches:
        fpath, plugin = match
        plugin_obj = plugin.spawn()
        subcommands = plugin_obj.get_subcommands()
        if subcommands:
            print ' ', fpath2namespace(fpath).upper()+':',str(tuple(subcommands)).replace("'",'')

        plugin_obj.help(indent=3)


def handle_main_argument(args, options):
    """ get a subparser and dispatch """

    ## Just subcomand name or "help"
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
            reporpt('Code not retrieve "plugin" from {mod}',mod=plugin_mod)
            sys.exit()
        plugin_obj = plugin.spawn()
        args  = args[1:] # cut off plugin name
        args  = filter(lambda x: not x.startswith('--'),args)
        plugin_obj.parse_args(args, options)

def entry():
    """ """
    if "--help" in sys.argv:
        show_all_plugins(); sys.exit()
    else:
        p=parser()
        (options, args) = p.parse_args()
        handle_main_argument(args, options)

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
