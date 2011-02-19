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

DEFAULT_WORKSPACE_NAME = 'kbk.workspace'
USAGE                  = "codebase subparser usage "

def map_over_files(func):
    """ """
    def likefilelines(self, *args,**kargs):
        """ """
        return dict( [ [fpath, func(fpath)] for fpath in self.files(*args, **kargs) ] )
    return likefilelines


class CodeBase(CBContext, Sandbox, CBPlugin):
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


    def restructure(self, pattern,goal, rules):
        """ proxy to rope """
        strukt  = restructure.Restructure(self.project, pattern, goal, rules)
        return strukt

    def get_changes(self,pattern, goal, rules):
        """ proxy to rope """
        return self.restructure(pattern, goal, rules).get_changes()

    def _search(self, name):
        """  internal search method
               NOTE: example_rules = {'s': {'type': '__builtins__.str','unsure': True}})
        """
        def get_matches(sections):
            """ obtain match objections inside sections """
            matches  = []
            for diff_marker, line in sections:
                junk1, data1,data2, junk2 = diff_marker.split()
                lineno  = data1.replace('-','').split(',')[0]
                lineno  = int(lineno)
                lineno += 3
                match   = dict( real_path = real_path,   # actually it's pth_shadow-relative
                                line=line[1:],           # snips off the "-" from the diff
                                lineno=lineno, )         # fully adjusted.
                matches.append(match)
            return matches

        pattern, goal, rules = name, '', {}

        ## Mirror code-files-only into the sandbox
        self.snapshot()

        ## Setup and grab data from rope-restructuring
        #strukt  = restructure.Restructure(self.project, pattern, goal, rules)
        #changes = strukt.get_changes()
        #strukt  = self.restructure(pattern,goal,rules)
        changes = self.get_changes(pattern,goal,rules)


        descr   = changes.description
        out     = dict( pattern=pattern, goal=goal, rules=rules,
                        descr=descr, changes=changes,)

        ## Build match-dictionaries with line numbers, etc
        real_changes  = changes.changes
        if real_changes:
            change_map = []
            for change_contents in real_changes:
                real_path  = change_contents.resource.real_path
                name       = path(real_path).name
                udiff      = change_contents.get_description().split('\n')

                do_test = lambda line: \
                          line.startswith('@@') or \
                          (line.startswith('-') and \
                           not line.startswith('---'))
                mdiff   = [ line for line in udiff if do_test(line) ]

                if len(mdiff) %2 != 0:
                    raise ValueError, "expected mdiff would be divisible by two."

                sections = groupby(mdiff, 2)
                matches  = get_matches(sections)
                result   = dict( real_path = real_path,
                                 name      = name,
                                 matches   = matches,
                                 diff      = udiff, )
                change_map.append(result)
            out.update(change_map=change_map)

        out.update(dict(moved = changes.get_changed_resources()))
        return out
