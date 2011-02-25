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

class Pythoscope(CLI):
    """ """

    codebase = None

    @classmethod
    def spawn(kls, **kargs):
        return Pythoscope()

    tests_folder = property(lambda self: self.codebase and path(self.codebase.pth_shadow)+path('/tests'))
    tests_files  = property(lambda self: self.tests_folder and self.tests_folder.files())

    @publish_to_commandline
    def generate(self, input_file_or_dir, imports=False):
        """ Generates empty unittests from project at @input_file_or_dir.
            If input is a single file, the result will be sent to stdout.
        """

        from kinbaku.codebase import plugin as CodeBase
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            self.codebase = codebase
            try:
                fpath = codebase.python_files[0]
            except IndexError:
                report(str(codebase.python_files))
            else:
                fpath     = codebase%fpath
                fpath     = path(fpath)
                container = fpath.parent

                self.init_pyscope(container)
                self.make_tests()

                # copy imports
                if imports:
                    imports_per_file = [ [_file, pygrep(_file, "imports",raw_text=True)] for _file in self.codebase.python_files ]
                    imports_per_file = dict(imports_per_file)
                else:
                    imports_per_file = {}

                #import IPython;IPython.Shell.IPShellEmbed(argv=[])()
                # If there's only file, display it to stdout
                if len(codebase.files())==1:
                    only_file = self.tests_files[0]
                    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
                    if imports_per_file:
                        print '""" {P}\n\n      tests for {fname} \n"""'.format(P=path(only_file).namebase, fname=input_file_or_dir)
                        #print "# <AutoImports>"
                        print imports_per_file.values()[0]
                        #print "# </AutoImports>"
                    print open(only_file).read()
                else:
                    raise Exception, NotImplemented

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

    def __init__(self, fpath=None):
        pass #self.fpath=fpath or self.default_fpath

plugin = Pythoscope
