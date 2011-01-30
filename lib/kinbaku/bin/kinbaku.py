""" kinbaku.bin.kinbaku:  the command line script

        $ kinbaku code --path=$HOME/code --search foobar
        $ kinbaku code --path=$HOME/code --search foobar --rules inst:xyz

        $ kinbaku detect --path=$HOME/code --tests

        $ kinbaku validate --path=$HOME/code

"""

from kinbaku.util import divider, remove_recursively, report, is_python, groupby, _import

from optparse import OptionParser
parser = OptionParser()
#parser.add_option("-f", "--file", dest="filename", help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
parser.add_option("-s", "--search", dest="search", default=True, help="..")
parser.add_option("-p", "--path", dest="path",  default='', help="..")
USAGE="WRITE ME"

def handle_main_argument(args,option):
    """ """
    main = args[0]
    try:
        codebase = _import('kinbaku.codebase')
    except ImportError:
        codebase.parse_args(options, args)
    else:
        print "Module not avail"

(options, args) = parser.parse_args()
if not args:
    print USAGE

elif len(args)==1:
    handle_main_argument(args,options)
else:
    print USAGE
