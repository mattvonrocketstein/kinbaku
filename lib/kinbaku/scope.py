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

class PythoscopeVox:
    """ a place for pythoscope to talk out into """
    @staticmethod
    def pythoscope_vox(*args, **kargs):
        report('   ',*args, **kargs)
    write = pythoscope_vox
from pythoscope import logger
from pythoscope import init_project
logger.set_output(PythoscopeVox)

class Pythoscope(KinbakuPlugin):
    """ """
    @classmethod
    def spawn(kls, **kargs):
        return Pythoscope()

    @publish_to_commandline
    def generate(self, input_dir):
        """ generates empty unittests from project-root at @input_dir
        """
        from kinbaku.codebase import plugin as CodeBase
        with CodeBase(input_dir, gloves_off=True, workspace=None) as codebase:
            # mirror fpath into codebase and get it's name
            #codebase.mirror()
            fpath = codebase.python_files[0]
            fpath = codebase%fpath
            fpath = path(fpath)
            fpath = fpath.parent
            self.init_pyscope(fpath)
            self.make_tests(codebase)

        sys.exit()

    def make_tests(self, codebase):
        files = codebase.python_files
        files = [codebase%fpath for fpath in files]
        from pythoscope import generate_tests
        generate_tests(files, force=False, template='unittest')

    def init_pyscope(self, fpath):
        """ initialize pyscope with codebase"""
        pythoscope_workspace = (fpath + path('/.pythoscope'))
        if pythoscope_workspace.exists():
            from kinbaku.util import remove_recursively
            remove_recursively(pythoscope_workspace)
        init_project(fpath)

    def __init__(self, fpath=None):
        pass #self.fpath=fpath or self.default_fpath
plugin = Pythoscope



def main():
    """ SRC: copied nearly verbatim from pythoscope.__init__.py
    """
    appname = os.path.basename(sys.argv[0])

    try:
        options, args = getopt.getopt(sys.argv[1:], "fhit:qvV",
                        ["force", "help", "init", "template=", "quiet", "verbose", "version"])
    except getopt.GetoptError, err:
        log.error("%s\n" % err)
        print USAGE % appname
        sys.exit(1)

    force = False
    init = False
    template = "unittest"

    for opt, value in options:
        if opt in ("-f", "--force"):
            force = True
        elif opt in ("-h", "--help"):
            print USAGE % appname
            sys.exit()
        elif opt in ("-i", "--init"):
            init = True
        elif opt in ("-t", "--template"):
            template = value
        elif opt in ("-q", "--quiet"):
            log.level = logger.ERROR
        elif opt in ("-v", "--verbose"):
            log.level = logger.DEBUG
        elif opt in ("-V", "--version"):
            print "%s %s" % (appname, __version__)
            sys.exit()

    try:
        if init:
            if args:
                project_path = args[0]
            else:
                project_path = "."
            init_project(project_path)
        else:
            if not args:
                log.error("You didn't specify any modules for test generation.\n")
                print USAGE % appname
            else:
                generate_tests(args, force, template)

    except KeyboardInterrupt:
        log.info("Interrupted by the user.")
    except Exception: # SystemExit gets through
        log.error("Oops, it seems that an internal Pythoscope error occurred. Please file a bug report at %s\n" % BUGTRACKER_URL)
        raise
