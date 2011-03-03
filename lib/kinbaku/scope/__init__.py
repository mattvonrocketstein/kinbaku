""" kinbaku.scope

      Pythoscope plugin

"""
import textwrap
import sys
import json
import os
from path import path
import logging

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.scope.cli import CLI
from kinbaku.util import remove_recursively
from kinbaku.pygrep import pygrep
from kinbaku.core import KinbakuFile
from pythoscope.generator import name2testname
#from kinbaku._sourcecodegen import CodeStream
from kinbaku._sourcecodegen import INDENTION

TEST_PREFIX = name2testname(' ').strip()
class Algebra:
    def map(self):
        """ returns {codebase-file:generated-test-file,}

            NOTE: this function is useless before self.make_tests() is called
            see also: self.__add__
        """
        codebasefiles = [ codebasefile.abspath() for codebasefile in self.codebase.files() ]
        codebasefiles = [ [codebasefile, self+codebasefile] for codebasefile in codebasefiles]
        return dict(codebasefiles)

    def __rshift__(self, fpath):
        """ operator to get src code for fpath:

              similar to:
                x = {codebase-file:generate-test-file,}[fpath]
                return open(x).read()

            returns None if it can't map "fpath" to a testfile.
        """
        fpath = path(fpath).abspath()
        out = self.map().get(fpath, None)
        return out and open(out).read()

    def __getitem__(self, slyce):
        """ Examples:

            self[fname:func_name] -->
              src_code for corresponding test function

            self[fname::func_name] -->
              src_code for function test function was generated from
        """
        from pythoscope.generator import find_method_code
        from pythoscope.astbuilder import parse
        if not isinstance(slyce, slice):
            raise Exception,NotImplementedYet
        fpath,y,z = slyce.start,slyce.stop,slyce.step
        if y:
            out = find_method_code(parse(self>>fpath), y)
        elif z:
            out = find_method_code(parse(open(fpath).read()), z)

        if not out:
            raise Exception,NotImplementedYet
        out = str(out).replace('"""',"'").split('\n')
        def x(line):
            if line.strip(): return INDENTION*2 + line
            else: return INDENTION*2+line
        out = [ x(line) for line in out]
        return '\n'.join(out)

class Wrapper(Algebra):
    """ Kinbaku wrapper for default pythoscope functionality
        adds features like file header, copying all imports,
        and better dynamic analysis.
    """
    tests_folder = lambda self: self.codebase and path(self.codebase.pth_shadow) + path('/tests')
    tests_folder = property(tests_folder)

    @property
    def tests_files(self):
        """  all this is really just in case there are
             stale files in the codebase.. shouldn't happen """
        if self.tests_folder:
            expected = [t.basename() for t in self.codebase.python_files]
            actual   = [ t.basename() for t in self.tests_folder.files()]
            transformed = [name2testname(x) for x in expected]
            if not transformed==actual:
                difference = set(transformed)-set(actual)
                raise Exception, 'expected tests would be related to original codebase'+difference
            return self.tests_folder.files()
        else:
            return []
    test_files = tests_files

    def make_tests(self):
        """ self.tests_files[0].startswith(self.codebase.project.address)
            self.tests_files[0][len(self.codebase.project.address):]
        """
        remove_recursively(self.tests_folder)
        #remove_recursively(self.tests_folder)
        files = self.codebase.python_files
        files = [self.codebase%fpath for fpath in files]
        from pythoscope import generate_tests
        generate_tests(files, force=False, template='unittest')

    def init_pyscope(self, fpath):
        """ initialize pythoscope with codebase
             ( will be <codebase-shadow>/.pythonscope )
        """
        from pythoscope import init_project
        self.workspace = (fpath + path('/.pythoscope'))
        if self.workspace.exists():
            report("Workspace exists.. wiping it")
            from kinbaku.util import remove_recursively
            remove_recursively(self.workspace)
        init_project(fpath)

class Pythoscope(CLI, Wrapper):

    codebase = None

    @classmethod
    def spawn(kls, **kargs):
        return Pythoscope()


    def __add__(self, other):
        """ converts to-be-tested-file in the real world
            into the corresponding generated-test-file
            in the shadow world
        """
        assert isinstance(other,str), str(NotImplementedYet)
        _map  = [ [path(tf).basename()[len(TEST_PREFIX):], path(tf).abspath()] for tf in self.tests_files ]
        _map  = dict(_map)
        bname = path(other).basename()
        if bname in _map:
            return _map.get(bname)

    def _generate(self, input_file_or_dir, imports=True, codebase=None):
        """ from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        """
        if not path(input_file_or_dir).isfile():
            # there are various ways that make_tests can bomb in pythoscope.. it's
            # really better to do this on a file by file basis.  in other words,
            # it may be  better to call "self" repeatedly rather than rely on
            # pythoscopes batch processing?
            print "Multiple files are not yet supported"
            sys.exit(1)
        fpath     = codebase % codebase.python_files[0]
        fpath     = path(fpath).abspath()
        container = (fpath.isdir() and fpath) or fpath.parent

        self.init_pyscope(container)
        self.make_tests()
        _map = self.map()
        one_argument = len(_map)==1
        _map = ( [fname, tname, self>>fname] for fname,tname in _map.items() )

        if one_argument:
            return _map #self >> _map.next()[0]
        else:
            raise Exception,'not supportd yet'
            #for fname,generated_test in _map:
            #    console.blue(fname); console.divider()
            #    print generated_test
            #    console.divider()

    @publish_to_commandline
    def generate(self, input_file_or_dir, originals=True, imports=True):
        """ Generates empty unittests from project at @input_file_or_dir.
            If input is a single file, the result will be sent to stdout.
        """

        from kinbaku.codebase import plugin as CodeBase
        postprocessors = []
        if imports: postprocessors.append(self.imports)
        if originals: postprocessors.append(self.originals)
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            if not codebase.python_files:
                report('No files')
                sys.exit(1)

            self.codebase = codebase
            results = self._generate(input_file_or_dir,imports=imports,codebase=codebase)

            for postprocessor in postprocessors:
                results = postprocessor(results)

            for fname,tname,generated_test in results:
                print generated_test


    def originals(self, results):
        """ original function implementation
            in test-function docstrings """
        from kinbaku._sourcecodegen import generate_code
        from kinbaku._ast import walkfunctions
        def cbf(fname):
            """ callback factory """
            results = []

            def callback(node, parent, lineage):
                original_code = self[fname::node.name[len(TEST_PREFIX):]]
                original_code = str(original_code)
                original_code = original_code#.lstrip().strip()
                original_code = [x for x in original_code.split('\n') if x]
                original_code = [' Original implementation:\n'] + \
                                [x for x in original_code]
                original_code = ('\n' ).join(original_code)
                node.doc = str(original_code)
                results.append( [node.name, generate_code(node)])
            return callback, results

        for fname, tfname, generated_test in results:
            cb1, results1 = cbf(fname)
            rrrr, root = walkfunctions(open(tfname).read(), cb1)

            yield fname,None, generate_code(root)


    def imports(self, results):
        """ copy imports from original file into test case """
        for fname, tname, generated_test in results:
            oldimports = pygrep(fname, "imports", raw_text=True)
            newtest = "{old_imports}\n{gtest}"
            newtest = newtest.format(old_imports = oldimports,
                                     gtest=generated_test)
            yield fname,tname, newtest

plugin = Pythoscope
if __name__=='__main__':
    pass
#from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
