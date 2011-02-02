import os

from kinbaku.report import console, report
from kinbaku.util import divider, remove_recursively
from kinbaku.plugin import KinbakuPlugin

from rope.contrib import generate
from rope.base.exceptions import RopeError

from kinbaku.plugin import KinbakuPlugin, publish_to_commandline
class CBPlugin(KinbakuPlugin):
    """

    @classmethod
    def hook(kls, args, options, name=None, path=None, **kargs):
        with kls(path, gloves_off=True) as codebase:
            try:
                func = getattr(codebase, name)
            except AttributeError:
                report("Plugin@{plugin} is not publishing a subparser for \"{name}\"",
                       plugin=codebase, name=name)
                sys.exit()
            report("running {f} with {a}, {k}",
                   f=func.__name__, a=args, k=options)
            result = func(*args)
            kls.display_results(result)

    @staticmethod
    def display_results(result):
       """ """
       if isinstance(result,list):
           report(*result)
       elif isinstance(result,dict):
           report(**result)
       else:
           report("Not sure how to deal with answer:", result)
    """
class CBContext(object):
    """ CodeBase-Aspect azucar syntactico: contextmanager protocol """
    def __exit__(self, type, value, tb):
        if self.debug: console.draw_line(msg=" __exit__ ")
        if not any([type, value, tb]):
            if self.debug:
                report("  closing project:", self.project.close())
                report("  removing shadow", remove_recursively(self.pth_shadow))
        else:
            report("exit with error", type, value, tb)

    def __enter__(self):
        """ """
        if self.debug:
            console.draw_line(msg="__enter__")
        return self

class Sandbox(object):
    """ CodeBase-Aspect Sandbox aspect of CodeBase """
    def __mod__(self,fpath):
        """ inverse of __getitem__, demirrors a fpath back into
            the original codebase.
        """
        raise NotImplemented

    def __getitem__(self,fpath):
        """ mirrors a fpath into sandbox:
              if this is called multiple times, it will get a fresh
              copy of the originating file each time..
        """
        if self.debug: report('mirroring "{fpath}" in sandbox', fpath=fpath.name)
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
