""" kinbaku.codebase.codebase
"""
import os
import compiler
import parser

import pylint
from path import path
from rope.base.project import Project
from rope.refactor import restructure

from kinbaku import analysis
from kinbaku.plugin import KinbakuPlugin
from kinbaku.util import report, is_python, groupby
from kinbaku.codebase.bases import Sandbox, CBContext
from kinbaku._types import UnusableCodeError
from kinbaku.plugin import publish_to_commandline

from kinbaku.codebase.cli import CBPlugin
from kinbaku.codebase.search import Search
from kinbaku.codebase.bases import RopeHelpers

DEFAULT_WORKSPACE_NAME = 'kbk.workspace'
USAGE                  = "codebase subparser usage "

def map_over_files(func):
    """ """
    def likefilelines(self, *args,**kargs):
        """ """
        return dict( [ [fpath, func(fpath)] for fpath in self.files(*args, **kargs) ] )
    return likefilelines

class CodeBase(CBContext, Sandbox, CBPlugin, Search, RopeHelpers):
    """ a thin wrapper on rope.base.project for easily working with sandboxes """

    debug          = False
    count_files    = property(lambda self: len(self.files()))
    count_py_files = property(lambda self: len(self.files(python=True)))
    count_lines    = property(lambda self: sum(self.file_lines(python=True).values()))
    file_lines     = map_over_files(analysis.count_lines)
    word_summary   = map_over_files(analysis.word_summary)
    file_comments  = map_over_files(analysis.get_comments)
    file_flakes    = map_over_files(analysis.pyflakes)

    def __init__(self, root, workspace=None, gloves_off=False, **rope_project_options):
        """ """
        def create_shadow(self):
            """ returns path to a shadow of root """
            name         = workspace or DEFAULT_WORKSPACE_NAME
            shade_holder = CodeBase.shadow_container()
            path         = os.path.join(shade_holder, name)

            if os.path.exists(path):
                if gloves_off:
                    if self.debug:
                        report("Gloves are off, killing ",path)
                    #remove_recursively(path)
                else:
                    err = "If the gloves aren't off, the shadow ({sh})should be uninhabited.."
                    raise Exception, err.format(sh=path)
            return path

        self.codex      = {} # Maps the shadow onto the real fs
        self.pth_root   = root
        self.pth_shadow = create_shadow(self)
        self.project    = Project(self.pth_shadow, **rope_project_options)

    def snapshot(self, static=True):
        """ take snapshot of current codebase """
        target_python_files = self.files(python=True)
        for fpath in target_python_files:
            report("Copying fpath @ {fpath} into shadow".format(fpath=fpath))
            self>>fpath
        shadow_files  = path(self.pth_shadow).files()
        shadow_python = filter(is_python, shadow_files)
        for fpath in shadow_python:
            if fpath.basename() not in [x.basename() for x in target_python_files]:
                report("Removing stale file @ {fpath}".format(fpath=fpath))
                os.remove(fpath)

    def has_changed(self, fpath):
        """ answer whether has_changed(fpath) since list mirror """
        before       = open(fpath,'r').read()
        after        = open((self^fpath),'r').read()
        file_changed = not( before == after )
        ast_changed  = compiler.parse(before,'exec')==compiler.parse(after,'exec')

        out = dict( file_changed=file_changed,
                    ast_changed=ast_changed )
        return out

    @property
    def python_files(self):
        """ only python files in target dir """
        return self.files(python=True)

    def __iter__(self):
        """ azucar syntactico: iterator over all files """
        return iter(self.files())
