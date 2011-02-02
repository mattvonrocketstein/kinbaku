""" kinbaku.codebase.codebase
"""

import os, sys
import shutil
from tempfile import gettempdir
from contextlib import contextmanager

import pylint

import rope
from path import path
from rope.base.exceptions import RopeError
from rope.base.project import Project
from rope.refactor import restructure
from rope.contrib import generate

from kinbaku import analysis
from kinbaku.report import console
from kinbaku.types import Match

from kinbaku.util import divider, remove_recursively
from kinbaku.util import report, is_python, groupby, _import
from kinbaku.codebase.bases import CBPlugin, Sandbox, CBContext

USAGE = "codebase subparser usage "

def map_over_files(func):
    """ """
    def likefilelines(self, *args,**kargs):
        return dict( [ [fpath, func(fpath)] for fpath in self.files(*args, **kargs) ] )
    return likefilelines
from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
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

    @classmethod
    def spawn(kls, path=None, **kargs):
        """ """
        #from tempfile import mktemp
        #root = mktemp(dir=kls.shadow_container(), prefix='codebase_')
        #print kargs
        #sys.exit()
        assert path
        return kls(path,gloves_off=True)

    @publish_to_commandline
    def stats(self):
        """ interface: stats """
        from kinbaku.analysis import *
        ws = self.word_summary()
        ws.update(combine_word_summary(ws))
        words_in_all_files = [ ws[fpath].keys() for fpath in ws ]
        return dict( file_count    = self.count_files,
                     py_file_count = self.count_py_files,
                     lines_count  = self.count_lines,
                     word_summary  = ws,
                     valid=[pylint(fpath) for fpath in self.files(python=True)],
                    )

    def __init__(self, root, gloves_off=False, **rope_project_options):
        """ """
        def create_shadow(self):
            """ returns path to a shadow of root """
            name         = "xyz" # TODO: compute name
            shade_holder = CodeBase.shadow_container()
            path         = os.path.join(shade_holder, name)

            if os.path.exists(path):
                if gloves_off:
                    if self.debug: report("Gloves are off, killing ",path)
                    #remove_recursively(path)
                else:
                    err = "If the gloves aren't off, the shadow ({sh})should be uninhabited.."
                    raise Exception, err.format(sh=path)
            return path
        if not os.path.exists(root):
            raise Exception, "nonexistent path {p}".format(p=root)
        self.pth_root   = root
        self.pth_shadow = create_shadow(self)
        self.project    = Project(self.pth_shadow, **rope_project_options)

    @publish_to_commandline
    def files(self, python=False):
        """ returns a list path() objects """
        all_files = path(self.pth_root).files()
        if python:
            out = filter(is_python, all_files)
        else:
            out = all_files
        return out

    def __iter__(self):
        """ azucar syntactico: iterator over all files """
        return iter(self.files())

    @publish_to_commandline
    def search(self, name):
        """ interface: search codebase using <name> """
        result = self._search(name)

        out=[]
        for match1 in result.get('change_map',[]):
            for match2 in match1['matches']:
                out.append(Match(search=name,**match2))
        return out


    def _search(self, name):
        """  internal search method
             NOTE: example_rules = {'s': {'type': '__builtins__.str','unsure': True}})
        """
        def get_matches(sections):
            """ """
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
        [ self[fpath] for fpath in self.files(python=True) ]

        ## Setup and grab data from rope-restructuring
        strukt  = restructure.Restructure(self.project, pattern, goal, rules)
        changes = strukt.get_changes()
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
