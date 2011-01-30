""" kinbaku: use cases for rope
"""
"""
mod1 = project.root.create_file('mod1.py')
mod1.write('def pow(x, y):\n    result = 1\n'
            '    for i in range(y):\n        result *= x\n'
            '    return result\n')
mod2 = project.root.create_file('mod2.py')
mod2.write('import mod1\nprint(mod1.pow(2, 3))\n')

from rope.refactor import restructure

pattern = '${pow_func}(${param1}, ${param2})'
goal = '${param1} ** ${param2}'
args = {'pow_func': 'name=mod1.pow'}

restructuring = restructure.Restructure(project, pattern, goal, args)

project.do(restructuring.get_changes())
mod2.read()
u'import mod1\nprint(2 ** 3)\n'

# Cleaning up
mod1.remove()
mod2.remove()
project.close()


        myfile = self.project.root.create_file('myfile.txt')
        self.assertEquals(myfile, path_to_resource(self.project,
                                                   myfile.real_path))
"""

from kinbaku.util import divider, report
from kinbaku.codebase import CodeBase


if __name__=="__main__":

    from kinbaku.util import divider, remove_recursively, report, is_python, groupby, _import
    USAGE="WRITE ME"
    def parser():
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename", help="use FILE", metavar="FILE")
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
        parser.add_option("-s", "--search", dest="search", default=True, help="..")
        parser.add_option("-p", "--path", dest="path",  default='', help="..")
        return parser

    def handle_main_argument(args,option):
        """ get a subparser and dispatch """
        main = args[0]
        try:
            plugin_mod = _import('kinbaku.{plugin}'.format(plugin=main))
        except ImportError,e:
            print "Plugin \"{p}\" not found: {e}".format(p=main,e=str(e))
        else:
            plugin = getattr(plugin_mod, 'plugin')
            plugin.parse_args(args[1:],options)

    (options, args) = parser().parse_args()
    if not args: print USAGE
    handle_main_argument(args,options)



    #codebox = '/home/matt/code/kinbaku/codebox'
    #with CodeBase(codebox, gloves_off=True) as codebase:
        #divider(msg='inside context')
        #report("codebase", codebase) #report("  test_files: "); report(*[fname for fname in codebase])
        #test_search = codebase.search("zam"); #report("  test_search: {results}",results=str(test_search))
        #import IPython;IPython.Shell.IPShellEmbed(argv=[])()
        #for x in test_search: print x
        #print 'next', codebase.next() #search(codebase, name)
