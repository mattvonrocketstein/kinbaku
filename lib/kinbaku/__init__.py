""" kinbaku: use cases for rope

This file is just used for scratch-work / notes


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
self.assertEquals(myfile, path_to_resource(self.project, myfile.real_path))
"""

def sig_example():
    from pep362 import signature
    def f(a,b,c): pass
    sig = signature(f)
    parameters = sig._parameters #{'a':parameter1,'b':parameter2, .. }
    print sig, parameters
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

if __name__=='__main__':
    sig_example()
