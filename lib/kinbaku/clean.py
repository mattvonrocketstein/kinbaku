""" kinbaku.clean
"""
import sys
from path import path

from kinbaku.report import console, report
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
from kinbaku.codebase import plugin as CodeBase
from kinbaku._types import Comment

class Cleaner(KinbakuPlugin):
    """ """

    @classmethod
    def spawn(kls, **kargs):
        return Cleaner()

    @publish_to_commandline
    def imports(self, input_file_or_dir):
        """ cleans and reorganizes module imports..
        """
        from rope.refactor.importutils import ImportTools, importinfo, add_import
        input_file_or_dir = path(input_file_or_dir)
        with CodeBase(input_file_or_dir, gloves_off=True, workspace=None) as codebase:
            pycore = codebase.project.pycore
            pymod  = pycore.resource_to_pyobject(codebase>>input_file_or_dir)
            x = ImportTools(codebase.project.pycore).organize_imports(pymod, unused=False)
            print x

plugin = Cleaner
