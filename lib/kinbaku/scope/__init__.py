""" kinbaku.scope

      Pythoscope plugin

"""
import sys
import json
import os
from path import path
import logging

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.scope.cli import CLI

from kinbaku.pygrep import pygrep

from pythoscope.generator import name2testname

class Wrapper:
    """ Kinbaku wrapper for default pythoscope functionality
        adds features like file header, copying all imports,
        and better dynamic analysis.
    """
    tests_folder = property(lambda self: self.codebase and path(self.codebase.pth_shadow) + path('/tests'))

    @property
    def tests_files(self):
        """  all this is really just in case there are
             stale files in the codebase.. shouldn't happen """
        if self.tests_folder:
            expected = [t.basename() for t in self.codebase.python_files]
            actual   = [ t.basename() for t in self.tests_folder.files()]
            transformed = [name2testname(x) for x in expected]
            if not transformed==actual:
                raise Exception,'expected tests would be related to original codebase'
            return self.tests_folder.files()
        else:
            return []
    test_files = tests_files

    def make_tests(self):
        """ self.tests_files[0].startswith(self.codebase.project.address)
            self.tests_files[0][len(self.codebase.project.address):]
        """
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
            from kinbaku.util import remove_recursively
            remove_recursively(self.workspace)
        init_project(fpath)

class Pythoscope(CLI, Wrapper):

    codebase = None

    @classmethod
    def spawn(kls, **kargs):
        return Pythoscope()


    @publish_to_commandline
    def generate(self, input_file_or_dir, imports=True):
        """ Generates empty unittests from project at @input_file_or_dir.
            If input is a single file, the result will be sent to stdout.
        """

        from kinbaku.codebase import plugin as CodeBase
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            if codebase.python_files:
                self.codebase = codebase
                self._generate(input_file_or_dir,imports=imports,codebase=codebase)
            else:
                report(str(codebase.python_files))

    def _generate(self, input_file_or_dir, imports=True, codebase=None):
        """ from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        """
        fpath     = codebase % codebase.python_files[0]
        fpath     = path(fpath).abspath()
        container = (fpath.isdir() and fpath) or fpath.parent

        self.init_pyscope(container)
        self.make_tests()

        # copy imports from original file into test case
        if imports:
            imports_per_file = [ [_file, pygrep(_file, "imports", raw_text=True)] for _file in self.codebase.python_files ]
            imports_per_file = dict(imports_per_file)
        else:
            imports_per_file = {}

        # If there's only file, display it to stdout
        if len(codebase.files())==1:
            only_file = self.tests_files[0]
            if imports_per_file:
                print '""" {P}\n\n      tests for {fname} \n"""'.format(P=path(only_file).namebase, fname=input_file_or_dir)
                print imports_per_file.values()[0]
            print open(only_file).read()
        else:
            raise Exception, NotImplemented

    def __init__(self, fpath=None):
        pass #self.fpath=fpath or self.default_fpath

plugin = Pythoscope
