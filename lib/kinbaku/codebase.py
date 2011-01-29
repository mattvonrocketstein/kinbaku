""" kinbaku.codebase:
      a thin wrapper on rope.base.project for easily working with sandboxes
"""

import os, sys
import shutil
from tempfile import gettempdir
from contextlib import contextmanager

import rope
from path import path
from rope.base.exceptions import RopeError
from rope.base.project import Project
from rope.refactor import restructure
from rope.contrib import generate

from kinbaku.report import console
from kinbaku.util import divider, remove_recursively, report, is_python, groupby

class Match(object):
    def __str__(self):
        return console.color(str(self.__dict__)).strip()
    __repr__=__str__
    def __init__(self, **kargs):
        for k,v in kargs.items(): setattr(self,k,v)

class CodeBaseContext(object):
    """ azucar syntactico: contextmanager protocol """

    def __exit__(self, type, value, tb):
        divider(msg=" __exit__ ")
        if not any([type, value, tb]):
            report("  closing project:", self.project.close())
            report("  removing shadow", remove_recursively(self.pth_shadow))
        else:
            report("exit with error", type, value, tb)

    def __enter__(self):
        """ """
        divider(msg="__enter__")
        report("  running _open")
        return self

class CodeSandbox(object):
    """ """
    def __mod__(self,fpath):
        """ inverse of __getitem__, demirrors a fpath back into
            the original codebase.
        """

    def __getitem__(self,fpath):
        """ mirrors a fpath into sandbox:
              if this is called multiple times, it will get a fresh
              copy of the originating file each time..
        """
        report('mirroring "{fpath}" in sandbox', fpath=fpath.name)
        namebase = fpath.namebase
        try:
            mod = generate.create_module(self.project, namebase)
        except RopeError,e:
            if "already exists" in str(e):
                ## Should not get here because we're wiping existing projects, right?
                name_would_be = os.path.join(self.pth_shadow, fpath.name)
                if os.path.exists(name_would_be):
                    remove_recursively(name_would_be)
                    return self[fpath]
                else:
                    raise Exception,['wait, what?', str(e), name_would_be]
            else:
                raise e
        else:
            mod.write(open(fpath).read())
            return mod

    @classmethod
    def shadow_container(kls):
        """ returns path to folder that will hold the shadows

        HACK: Using ``/dev/shm/`` for faster tests
        """
        if os.name == 'posix' and os.path.isdir('/dev/shm'):
            return '/dev/shm/'
        else:
            return gettempdir()


class CodeBase(CodeBaseContext, CodeSandbox):
    """ a thin wrapper on rope.base.project for easily working with sandboxes """


    @classmethod
    def spawn(kls):
        """ """
        from tempfile import mktemp
        root = mktemp(dir=kls.shadow_container(), prefix='codebase_')
        return kls(root)

    def __init__(self, root, gloves_off=False, **rope_project_options):
        """ """

        def create_shadow(self):
            """ returns path to a shadow of root """
            name         = "xyz" # TODO: compute name
            shade_holder = CodeBase.shadow_container()
            path         = os.path.join(shade_holder, name)

            if os.path.exists(path):
                if gloves_off:
                    report("Gloves are off, killing ",path)
                    #remove_recursively(path)
                else:
                    raise Exception, "If the gloves aren't off, the shadow should be uninhabited.."
            return path

        self.pth_root   = root
        self.pth_shadow = create_shadow(self)
        self.project    = Project(self.pth_shadow, **rope_project_options)

    def files(self, python=False):
        """ returns a list path() objects """
        all_files = path(self.pth_root).files()
        if python:
            out = filter(is_python, all_files)
        else:
            out = all_files
        return out

    def __iter__(self):
        return iter(self.files())

    def search(self, name):
        result = self._search(name)

        out=[]
        for match1 in result['change_map']:
            for match2 in match1['matches']:
                out.append(Match(search=name,**match2))
        return out


    def _search(self, name):
        """  internal search method
             NOTE: example_rules = {'s': {'type': '__builtins__.str','unsure': True}})
        """
        pattern = name
        goal    = ''
        rules   = {}
        args    = [ self.project, pattern, goal, rules ]
        for fpath in self.files(python=True):
            mod = self[fpath]
        strukt  = restructure.Restructure(*args)
        changes = strukt.get_changes()
        descr   = changes.description
        out = dict( pattern=pattern, goal=goal, rules=rules,
                    descr=descr, changes=changes,)

        ## Build match-dictionaries with line numbers, etc
        real_changes  = changes.changes
        if real_changes:
            change_map = []
            for change_contents in real_changes:
                real_path  = change_contents.resource.real_path
                name       = path(real_path).name
                udiff      = change_contents.get_description().split('\n')
                matches = []
                mdiff = [line for line in udiff if line.startswith('@@') or (line.startswith('-') and not line.startswith('---'))]
                if len(mdiff)%2!=0:
                    raise ValueError, "expected mdiff would be divisible by two."

                sections = groupby(mdiff,2)
                for diff_marker, line in sections:
                    junk1, data1,data2, junk2 = diff_marker.split()
                    lineno  = data1.replace('-','').split(',')[0]
                    lineno  = int(lineno)
                    lineno += 3
                    match   = dict(real_path = real_path,   # actually it's pth_shadow-relative
                                   line=line[1:],           # snips off the "-" from the diff
                                   lineno=lineno,           # fully adjusted.
                                   )
                    matches.append(match)

                change_map.append(dict(real_path = real_path,
                                       name = name,
                                       matches = matches,
                                       #subtraction = subtraction,
                                       #src=src, dst=dst,
                                      diff = udiff))
            out.update(change_map=change_map)
        out.update(dict(moved = changes.get_changed_resources()))
        return out
