""" kinbaku.bin.kinbaku:  the command line script

    $ kinbaku code --path=$HOME/code --search foobar
    $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

    $ kinbaku detect --path=$HOME/code --tests

    $ kinbaku validate --path=$HOME/code

"""
import copy, sys
from path import path
import kinbaku
from kinbaku.util import divider, remove_recursively, report, is_python, groupby, _import


USAGE="""
kinbaku is a tool for static analysis of python source files.

    $ kinbaku code --path=$HOME/code --search foobar
    $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

    $ kinbaku detect --path=$HOME/code --tests

    $ kinbaku validate --path=$HOME/code

"""
def parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="use FILE", metavar="FILE")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
    parser.add_option("-s", "--search", dest="search", default=True, help="..")
    parser.add_option("-p", "--path", dest="path",  default='', help="..")
    return parser
def plugin_search_results():
    """ """
    plugins         = []
    fileself        = path(__file__).abspath()
    container       = fileself.dirname().dirname().abspath()
    container_files = [ x for x in container.files() if x.abspath()!=fileself]
    container_files = [ x for x in container_files if x.ext == '.py']
    for fpath in container_files:
        reality    = globals()
        shadow     = copy.copy(globals())
        shadow.update(dict(__name__='__shadow__'))
        execfile(fpath, shadow)
        difference = list(set(shadow.keys())-set(reality.keys()))
        if "plugin" in difference:
            plugin_obj = shadow['plugin']
            plugins.append([fpath, plugin_obj])
            #print "\tfound plugin",fpath,plugin_obj, plugin_obj.__class__.__bases__
    return plugins

def show_all_plugins():
    """ displays all plugins and their
        options in an easy to read menu """
    matches = plugin_search_results()
    for match in matches:
        print
        fpath, plugin = match
        print ':',plugin.__name__.upper()
        plugin().help()


def handle_main_argument(args, options):
    """ get a subparser and dispatch """

    try: main = args[0]
    except IndexError:
        show_all_plugins()
        sys.exit()
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
        plugin().parse_args(args[1:], options)

def entry():
    """ """
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
