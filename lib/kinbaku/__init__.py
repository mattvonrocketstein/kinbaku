""" kinbaku: use cases for rope
"""
import os
import rope
from path import path
from rope.base.project import Project
from rope.refactor import restructure
from rope.contrib import generate

from kinbaku.tools import remove_recursively
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
"""
from tempfile import gettempdir
from contextlib import contextmanager

class CodeBase(object):
    """
    # Using these prefs for faster tests
    prefs = {'save_objectdb': False, 'save_history': False,
             'validate_objectdb': False, 'automatic_soa': False,
             'ignored_resources': ['.ropeproject', '*.pyc'],
             'import_dynload_stdmods': False}
    prefs.update(kwds)
    remove_recursively(root)
    project = rope.base.project.Project(root, **prefs)
    return project

    """

    def __init__(self, root, gloves_off=False, **rope_project_options):
        """ """
        def shadow_container(self):
            """ returns path to folder that will hold the shadows

                HACK: Using ``/dev/shm/`` for faster tests
            """
            if os.name == 'posix' and os.path.isdir('/dev/shm'):
                return '/dev/shm/'
            else:
                return gettempdir()

        def create_shadow(self):
            """ returns path to a shadow of root """
            name         = "xyz" # TODO: compute name
            shade_holder = shadow_container(self)
            path         = os.path.join(shade_holder, name)

            if os.path.exists(path):
                if gloves_off:
                    print "\tGloves are off, killing ",path
                    #remove_recursively(path)
                else:
                    raise Exception, "If the gloves aren't off, the shadow should be uninhabited.."
            return path

        print '__init__'
        self.pth_root   = root
        self.pth_shadow = create_shadow(self)
        self.project    = Project(self.pth_shadow, **rope_project_options)

    def __exit__(self, type, value, tb):
        """ azucar syntactico: contextmanager protocol """
        divider()
        print '__exit__'
        if not any([type, value, tb]):
            self._close()
        else:
            msg = str(["exit with error", type, value, tb])
            print msg
            #print dir(tb)

    def _close(self):
        """ """
        print "\trunning _close"
        print " \tclosing project:", self.project.close()
        print "\tremoving shadow", remove_recursively(self.pth_shadow)

    def _open(self):
        print "\trunning _open"

    def __enter__(self):
        """ """
        divider(); print "__enter__"
        self._open()
        return self

    def files(self):
        return path(self.pth_root).files()

    def __iter__(self): return iter(self.files())

    def search(self, name):
        """
             ie, options = {'s': {'type': '__builtins__.str','unsure': True}})
        """
        pattern = name
        goal    = ''
        rules   = {}
        args    = [ self.project, pattern, goal, rules ]

        for fpath in self.files():
            #pass
            #clone = self[fpath]
            mod = generate.create_module(self.project, fpath.name)
            raise Exception,mod
        strukt  = restructure.Restructure(*args)
        changes = strukt.get_changes()
        descr   = changes.description
        moved   = changes.get_changed_resources()
        return moved #dir(changes) #changes

def divider():
    print "-"*80

if __name__=="__main__":
    import pprint
    codebox = '/home/matt/code/kinbaku/codebox'
    with CodeBase(codebox,gloves_off=True) as codebase:
        divider()
        print "inside context, with codebase", codebase #
        test_search = codebase.search("test_name")
        print "\t test_files: ", [fname for fname in codebase]
        print "\t test_search: ", pprint.pprint(test_search)
        import IPython;IPython.Shell.IPShellEmbed(argv=[])()


        #print 'next', codebase.next() #search(codebase, name)
        #print 'next', codebase.next() #search(codebase, name)
