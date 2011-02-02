""" kinbaku.bin.kinbaku:  the command line script

    $ kinbaku code --path=$HOME/code --search foobar
    $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

    $ kinbaku detect --path=$HOME/code --tests

    $ kinbaku validate --path=$HOME/code

"""
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

def handle_main_argument(args, options):
    """ get a subparser and dispatch """
    main = args[0]
    try:
        plugin_mod = _import('kinbaku.{plugin}'.format(plugin=main))
    except ImportError,e:
        print "Plugin \"{p}\" not found: {e}".format(p=main,e=str(e))
    else:
        plugin = getattr(plugin_mod, 'plugin',None)
        if not plugin:
            report('Code not retrieve "plugin" from {mod}',mod=plugin_mod)
            sys.exit()
        plugin.parse_args(args[1:],options)

def entry():
    """ """
    (options, args) = parser().parse_args()
    if not args:
        print USAGE
    else:
        handle_main_argument(args,options)



#codebox = '/home/matt/code/kinbaku/codebox'
#with CodeBase(codebox, gloves_off=True) as codebase:
#divider(msg='inside context')
#report("codebase", codebase) #report("  test_files: "); report(*[fname for fname in codebase])
#test_search = codebase.search("zam"); #report("  test_search: {results}",results=str(test_search))
#import IPython;IPython.Shell.IPShellEmbed(argv=[])()
#for x in test_search: print x
#print 'next', codebase.next() #search(codebase, name)
