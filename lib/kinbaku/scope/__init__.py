""" kinbaku.scope

      Pythoscope plugin

"""
import textwrap
import sys
import json
import os
from path import path
import logging

from pythoscope.generator import name2testname

from kinbaku.report import console, report
from kinbaku.scope.cli import CLI
from kinbaku.pygrep import pygrep
from kinbaku.core import KinbakuFile
from kinbaku.python import Dotpath
from kinbaku.python import PythonModule
from kinbaku.scope.algebra import Algebra
from kinbaku.util import remove_recursively
from kinbaku.plugin import KinbakuPlugin
from kinbaku.plugin import publish_to_commandline

TEST_PREFIX = name2testname(' ').strip()

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

class PostProcessors(object):
    """ """
    def originals(self, results):
        """ original function implementation
            in test-function docstrings """

        from kinbaku._ast import walkfunctions, generate_code

        def cbf(fname):
            """ callback factory """
            results = []
            def callback(node, parent, lineage):
                """ for each function in the test file,
                    write into it's docstring the code
                    for the original function """
                original_code = self[fname::node.name[len(TEST_PREFIX):]]
                original_code = str(original_code)
                original_code = original_code.rstrip()
                original_code = [x for x in original_code.split('\n') if x]
                original_code = [' Original implementation:\n'] + \
                                [x for x in original_code]
                original_code = ('\n' ).join(original_code)
                node.doc = str(original_code)
                results.append( [node.name, generate_code(node)+'\n'])
            return callback, results

        for fname, tfname, generated_test in results:
            cb1, results1 = cbf(fname)
            _, root = walkfunctions(generated_test, cb1)
            code = generate_code(root)
            yield fname, tfname, code


    def imports(self, results):
        """ copy imports from original file into test case """
        for fname, tname, generated_test in results:
            oldimports = pygrep(fname, "imports", raw_text=True)
            newtest  = '""" {label}\n"""\n\nimport os; {tfile}\n\n## Begin: Original imports\n'
            newtest += '{old_imports}\n## Fin:   Original imports\n\n{gtest}'
            newtest  = newtest.format(label=Dotpath.from_fname(fname),
                                      old_imports = oldimports,
                                      tfile = "THIS_DIR = os.path.abspath(os.path.split(__file__)[0])",
                                      gtest = generated_test)
            yield fname, tname, newtest

    def examples(self, results):
        """ find examples for fach function if possible """
        for fname, tname, generated_test in results:

            pass

class Pythoscope(CLI, Wrapper, PostProcessors):

    codebase = None

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
        for fname,tname in _map.items():
            yield fname, tname, self>>fname


    @publish_to_commandline
    def generate(self, input_file_or_dir, originals=True, imports=True):
        """ Generates empty unittests from project at @input_file_or_dir.
            If input is a single file, the result will be sent to stdout.
        """

        from kinbaku.codebase import plugin as CodeBase

        postprocessors = []
        if originals: postprocessors.append(self.originals)
        if imports:   postprocessors.append(self.imports)

        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            if not codebase.python_files:
                report('No files')
                sys.exit(1)

            self.codebase = codebase
            results = self._generate(input_file_or_dir, imports=imports, codebase=codebase)

            for pp in postprocessors:
                results=pp([x for x in results])

            for fname,tname,generated_test in results:
                print generated_test
plugin = Pythoscope

if __name__=='__main__':
    pass
